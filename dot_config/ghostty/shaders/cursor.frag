// Ghostty Master Shader — Enhanced Aesthetics (Glowing Trailing Tail, Text Bloom, Vignette)

// Configurable Parameters:

// Animation duration in seconds (slower, liquid smooth).
const float duration_seconds = 0.38;

// Bloom / Glow strength around text (0.0 to disable, 0.10 for subtle modern glow).
const float bloom_strength = 0.10;

// Trailing tail glow brightness multiplier (glowing trail during movement).
const float trail_glow_intensity = 0.75;

// Vignette strength (0.0 to disable, 0.08 for subtle corner depth).
const float vignette_strength = 0.08;

// FIN

bool box_contains(const vec2 p, const vec4 bb) {
  return bb.x < p.x && p.x < bb.z && bb.y < p.y && p.y < bb.w;
}

vec4 bb(const vec4 rect) {
  return vec4(rect.xy - vec2(0, rect.w), rect.xy + vec2(rect.z, 0));
}

vec2 left_top(const vec4 bb)     { return bb.xy; }
vec2 left_bottom(const vec4 bb)  { return bb.xw; }
vec2 right_top(const vec4 bb)    { return bb.zy; }
vec2 right_bottom(const vec4 bb) { return bb.zw; }

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
  const vec4 color = texture2D(iChannel0, uv);
  frag_color = color;

  // 1. Subtle Text Bloom / Glow (OLED-style text radiance)
  if (bloom_strength > 0.0) {
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

  // 2. Animated Trailing Tail with Tail Glow (Zero glow on static cursor)
  if (iCurrentCursor.z > 0.0 && iCurrentCursor.w > 0.0 &&
      iPreviousCursor.z > 0.0 && iPreviousCursor.w > 0.0) {
    const vec4 curr = bb(iCurrentCursor);
    const vec4 prev = bb(iPreviousCursor);

    const vec2 curr_center = mix(curr.xy, curr.zw, 0.5);
    const vec2 prev_center = mix(prev.xy, prev.zw, 0.5);
    const vec2 diff = curr_center - prev_center;

    if (diff != vec2(0.0, 0.0)) {
      const float progress = min((iTime - iTimeCursorChange) * speed, 1.0);

      if (progress < 1.0) {
        // Silky non-linear ease-out curve (fast start, smooth liquid-like deceleration)
        const float t = 1.0 - pow(1.0 - progress, 3.5);

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
          vec3 trail_rgb = iCurrentCursorColor.rgb;
          // Guard: Ensure trail color is bright and vibrant
          if (length(trail_rgb) < 0.3) {
            trail_rgb = vec3(0.85, 0.82, 0.75); // Bright Morandi warm gold/iris
          }

          float fade = pow(1.0 - progress, 1.4);

          // 1. Solid alpha blend for the trail body
          vec4 trail_color = vec4(trail_rgb, fade * 0.90);
          frag_color = alpha_blend(trail_color, frag_color);

          // 2. Additive light emission along the trail for vibrant glowing radiance!
          frag_color.rgb += trail_rgb * fade * 0.50;
        }
      }
    }

    if (box_contains(frag_coord, curr)) {
      frag_color = color;
    }
  }

  // 3. Subtle Vignette (Darken corners slightly for immersive depth)
  if (vignette_strength > 0.0) {
    vec2 v_uv = uv * (1.0 - uv.yx);
    float vig = v_uv.x * v_uv.y * 15.0;
    vig = clamp(pow(vig, vignette_strength), 0.0, 1.0);
    frag_color.rgb *= vig;
  }
}
