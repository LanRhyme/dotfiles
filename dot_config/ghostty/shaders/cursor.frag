// Ghostty Master Shader — Fluid Liquid Cursor Trail, Zero-Distortion Character Entry & Fine Raindrop Ripple

// Configurable Parameters:

// Animation duration in seconds (slower, ultra-smooth fluid movement).
const float duration_seconds = 0.52;

// Bloom / Glow strength around text (0.0 to disable, 0.06 for subtle modern glow).
const float bloom_strength = 0.06;

// Vignette strength (0.0 to disable, 0.06 for subtle corner depth).
const float vignette_strength = 0.06;

// FIN

bool box_contains(const vec2 p, const vec4 bb) {
  return bb.x <= p.x && p.x <= bb.z && bb.y <= p.y && p.y <= bb.w;
}

// Convert Ghostty cursor rect vec4(x, y, w, h) to GLSL vec4(min_x, min_y, max_x, max_y)
vec4 bb(const vec4 rect) {
  return vec4(rect.x, rect.y - rect.w, rect.x + rect.z, rect.y);
}

vec2 left_top(const vec4 bb)     { return vec2(bb.x, bb.w); }
vec2 left_bottom(const vec4 bb)  { return vec2(bb.x, bb.y); }
vec2 right_bottom(const vec4 bb) { return vec2(bb.z, bb.y); }
vec2 right_top(const vec4 bb)    { return vec2(bb.z, bb.w); }

vec4 alpha_blend(const vec4 x, const vec4 y) {
  const float a = mix(x.a, 1.0, y.a);
  const vec3 rgb = mix(y.a * y.rgb, x.rgb, x.a) / a;
  return vec4(rgb, a);
}

bool quad_contains(const vec2 p, const vec2 a, const vec2 b, const vec2 c, const vec2 d) {
  const vec2 v0 = b - a;
  const vec2 v1 = c - b;
  const vec2 v2 = d - c;
  const vec2 v3 = a - d;

  const float d0 = determinant(mat2(p - a, v0));
  const float d1 = determinant(mat2(p - b, v1));
  const float d2 = determinant(mat2(p - c, v2));
  const float d3 = determinant(mat2(p - d, v3));

  const bool neg = d0 < 0.0 || d1 < 0.0 || d2 < 0.0 || d3 < 0.0;
  const bool pos = d0 > 0.0 || d1 > 0.0 || d2 > 0.0 || d3 > 0.0;

  return !(neg && pos);
}

const float speed = 1.0 / duration_seconds;

void mainImage(out vec4 frag_color, vec2 frag_coord) {
  const vec2 uv = frag_coord / iResolution.xy;

  // Check if window is focused and cursor is active
  bool is_focused = (iCurrentCursorColor.a > 0.1) && (iCurrentCursor.z > 0.0) && (iCurrentCursor.w > 0.0);

  const vec4 color = texture2D(iChannel0, uv);
  frag_color = color;

  const vec4 curr = bb(iCurrentCursor);
  const vec4 prev = bb(iPreviousCursor);

  const vec2 curr_center = mix(curr.xy, curr.zw, 0.5);
  const vec2 prev_center = mix(prev.xy, prev.zw, 0.5);
  const vec2 diff = curr_center - prev_center;

  // Detect focus loss / gain cursor shape transition (e.g. beam <-> hollow box)
  bool is_shape_change = (abs(iCurrentCursor.z - iPreviousCursor.z) > 2.0) || (abs(iCurrentCursor.w - iPreviousCursor.w) > 2.0);

  float type_time = (iTimeCursorChange > 0.0) ? (iTime - iTimeCursorChange) : 1.0;

  // 1. Newly Typed Character Entry Highlight (Zero distortion, zero interference to surrounding pixels)
  if (is_focused && !is_shape_change && type_time > 0.0 && type_time < 0.18) {
    if (box_contains(frag_coord, curr)) {
      float glow = exp(-type_time * 16.0) * 0.35;
      vec3 char_tint = iCurrentCursorColor.rgb;
      if (length(char_tint) < 0.3) { char_tint = vec3(0.85, 0.82, 0.75); }
      frag_color.rgb += char_tint * glow;
    }
  }

  // 2. Text Bloom / Glow (Only when window is focused)
  if (is_focused && bloom_strength > 0.0) {
    vec2 px = 1.5 / iResolution.xy;
    vec4 bloom_sum = texture2D(iChannel0, uv + vec2(-px.x, -px.y)) * 0.0625 +
                     texture2D(iChannel0, uv + vec2( 0.0,  -px.y)) * 0.125  +
                     texture2D(iChannel0, uv + vec2( px.x, -px.y)) * 0.0625 +
                     texture2D(iChannel0, uv + vec2(-px.x,   0.0)) * 0.125  +
                     texture2D(iChannel0, uv + vec2( 0.0,    0.0)) * 0.25   +
                     texture2D(iChannel0, uv + vec2( px.x,   0.0)) * 0.125  +
                     texture2D(iChannel0, uv + vec2(-px.x,  px.y)) * 0.0625 +
                     texture2D(iChannel0, uv + vec2( 0.0,   px.y)) * 0.125  +
                     texture2D(iChannel0, uv + vec2( px.x,  px.y)) * 0.0625;
    frag_color.rgb += bloom_sum.rgb * bloom_strength;
  }

  // 3. Animated Cursor Trailing Tail & Raindrop Water Ripple (Strictly when focused & active)
  if (is_focused && iPreviousCursor.z > 0.0 && iPreviousCursor.w > 0.0) {

    // Fine Raindrop Water Ripple on Keypress (Strictly on active typing, NOT on focus gain)
    if (!is_shape_change && type_time > 0.0 && type_time < 0.20) {
      float drop_t = type_time / 0.20;
      float dist = length(frag_coord - curr_center);

      // Raindrop radius: delicate 16px max expansion
      float primary_radius = drop_t * 16.0;

      // Super fine ring width
      float ring = exp(-pow(dist - primary_radius, 2.0) / 4.0);

      // Exponential water damping
      float water_fade = pow(1.0 - drop_t, 2.0);

      vec3 water_tint = iCurrentCursorColor.rgb;
      if (length(water_tint) < 0.3) { water_tint = vec3(0.82, 0.84, 0.80); }

      frag_color.rgb += water_tint * ring * water_fade * 0.18;
    }

    // Liquid Cursor Trailing Animation
    if (!is_shape_change && diff != vec2(0.0, 0.0) && length(diff) > 2.0) {
      const float progress = min((iTime - iTimeCursorChange) * speed, 1.0);

      if (progress < 1.0) {
        // High-order Quintic Ease-Out curve for ultra-silky fluid deceleration (0.52s)
        const float t = 1.0 - pow(1.0 - progress, 4.5);
        const float fade = pow(1.0 - progress, 1.5);

        vec3 trail_rgb = iCurrentCursorColor.rgb;
        if (length(trail_rgb) < 0.2) {
          trail_rgb = vec3(0.68, 0.67, 0.61);
        }

        // Tail corners receding from prev to curr
        const vec2 t_lt = mix(left_top(prev), left_top(curr), t);
        const vec2 t_lb = mix(left_bottom(prev), left_bottom(curr), t);
        const vec2 t_rb = mix(right_bottom(prev), right_bottom(curr), t);
        const vec2 t_rt = mix(right_top(prev), right_top(curr), t);

        // Head corners anchored tightly to curr
        const vec2 c_lt = left_top(curr);
        const vec2 c_lb = left_bottom(curr);
        const vec2 c_rb = right_bottom(curr);
        const vec2 c_rt = right_top(curr);

        // Check if pixel is within the seamless hull connecting tail to head
        bool in_trail = quad_contains(frag_coord, t_lt, t_lb, c_lb, c_lt) ||
                        quad_contains(frag_coord, t_lb, t_rb, c_rb, c_lb) ||
                        quad_contains(frag_coord, t_rb, t_rt, c_rt, c_rb) ||
                        quad_contains(frag_coord, t_rt, t_lt, c_lt, c_rt) ||
                        quad_contains(frag_coord, t_lt, t_lb, t_rb, t_rt);

        if (in_trail) {
          // Trail opacity tuned to 70% max
          vec4 trail_color = vec4(trail_rgb, fade * 0.70);
          frag_color = alpha_blend(trail_color, frag_color);
        }
      }
    }

    if (box_contains(frag_coord, curr)) {
      frag_color = color;
    }
  }

  // 4. Subtle Vignette (Darken corners slightly for immersive depth)
  if (vignette_strength > 0.0) {
    vec2 v_uv = uv * (1.0 - uv.yx);
    float vig = v_uv.x * v_uv.y * 15.0;
    vig = clamp(pow(vig, vignette_strength), 0.0, 1.0);
    frag_color.rgb *= vig;
  }
}
