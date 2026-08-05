// Ghostty Master Shader — Enhanced Aesthetics (Glowing Trailing Tail with Subtle Diffusion, Text Bloom, Vignette)

// Configurable Parameters:

// Animation duration in seconds (slower, ultra-smooth fluid movement).
const float duration_seconds = 0.52;

// Bloom / Glow strength around text (0.0 to disable, 0.06 for subtle modern glow).
const float bloom_strength = 0.06;

// Trailing tail light diffusion / scatter strength (faint & subtle, 0.08).
const float trail_diffusion_strength = 0.08;

// Vignette strength (0.0 to disable, 0.06 for subtle corner depth).
const float vignette_strength = 0.06;

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

float dist_to_segment(vec2 P, vec2 A, vec2 B) {
  vec2 AB = B - A;
  float len_sq = dot(AB, AB);
  if (len_sq == 0.0) return length(P - A);
  float t_proj = clamp(dot(P - A, AB) / len_sq, 0.0, 1.0);
  vec2 projection = A + t_proj * AB;
  return length(P - projection);
}

const float speed = 1.0 / duration_seconds;

void mainImage(out vec4 frag_color, vec2 frag_coord) {
  const vec2 uv = frag_coord / iResolution.xy;
  const vec4 color = texture2D(iChannel0, uv);
  frag_color = color;

  // Check if window is focused and cursor is active
  bool is_focused = (iCurrentCursorColor.a > 0.1) && (iCurrentCursor.z > 0.0) && (iCurrentCursor.w > 0.0);

  // 1. Text Bloom / Glow (Only when window is focused)
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

  // 2. Animated Trailing Tail (Strictly when focused & moving)
  if (is_focused && iPreviousCursor.z > 0.0 && iPreviousCursor.w > 0.0) {
    const vec4 curr = bb(iCurrentCursor);
    const vec4 prev = bb(iPreviousCursor);

    const vec2 curr_center = mix(curr.xy, curr.zw, 0.5);
    const vec2 prev_center = mix(prev.xy, prev.zw, 0.5);
    const vec2 diff = curr_center - prev_center;

    if (diff != vec2(0.0, 0.0) && length(diff) > 2.0) {
      const float progress = min((iTime - iTimeCursorChange) * speed, 1.0);

      if (progress < 1.0) {
        // High-order Quintic Ease-Out curve for ultra-silky, gradual deceleration (0.52s)
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
          // Reverted soft, elegant trail opacity (50% max)
          vec4 trail_color = vec4(trail_rgb, fade * 0.50);
          frag_color = alpha_blend(trail_color, frag_color);
        }

        // Faint, gentle 2D light diffusion strictly active during trail motion
        if (trail_diffusion_strength > 0.0) {
          vec2 tail_center = mix(prev_center, curr_center, t);
          float dist_seg = dist_to_segment(frag_coord, tail_center, curr_center);
          float scatter = exp(-dist_seg * 0.15) * fade * trail_diffusion_strength;
          frag_color.rgb += trail_rgb * scatter;
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
