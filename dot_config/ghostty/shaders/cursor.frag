// Ghostty Master Shader — Clean Smooth Liquid Cursor Trail (No Circles, No Distortion)

// Configurable Parameters:

// Animation duration in seconds (slower, ultra-smooth fluid movement).
const float duration_seconds = 0.52;

// Bloom / Glow strength around text (0.0 to disable, 0.06 for subtle modern glow).
const float bloom_strength = 0.06;

// Vignette strength (0.0 to disable, 0.06 for subtle corner depth).
const float vignette_strength = 0.06;

// FIN

bool box_contains(const vec2 p, const vec4 bb) {
  return bb.x < p.x && p.x < bb.z && bb.y < p.y && p.y < bb.w;
}

vec4 bb(const vec4 rect) {
  return vec4(rect.xy - vec2(0, rect.w), rect.xy + vec2(rect.z, 0));
}

vec4 alpha_blend(const vec4 x, const vec4 y) {
  const float a = mix(x.a, 1.0, y.a);
  const vec3 rgb = mix(y.a * y.rgb, x.rgb, x.a) / a;
  return vec4(rgb, a);
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

  // 2. Animated Pure Liquid Cursor Trail (Strictly when focused & moving)
  if (is_focused && iPreviousCursor.z > 0.0 && iPreviousCursor.w > 0.0) {
    const vec4 curr = bb(iCurrentCursor);
    const vec4 prev = bb(iPreviousCursor);

    const vec2 curr_center = mix(curr.xy, curr.zw, 0.5);
    const vec2 prev_center = mix(prev.xy, prev.zw, 0.5);
    const vec2 diff = curr_center - prev_center;

    // Detect focus loss / gain cursor shape transition (e.g. beam <-> hollow box)
    bool is_shape_change = (abs(iCurrentCursor.z - iPreviousCursor.z) > 2.0) || (abs(iCurrentCursor.w - iPreviousCursor.w) > 2.0);

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

        // Directional perpendicular thickness matching exact beam width vs cell height
        vec2 dir = normalize(diff);
        vec2 perp = vec2(-dir.y, dir.x);
        float half_thick = abs(perp.x) * (curr.z * 0.5) + abs(perp.y) * (curr.w * 0.5);
        half_thick = max(half_thick, 1.0);

        vec2 tail_center = mix(prev_center, curr_center, t);
        float dist_seg = dist_to_segment(frag_coord, tail_center, curr_center);

        if (dist_seg <= half_thick) {
          float edge_smooth = smoothstep(half_thick, max(0.0, half_thick - 1.0), dist_seg);
          vec4 trail_color = vec4(trail_rgb, fade * 0.70 * edge_smooth);
          frag_color = alpha_blend(trail_color, frag_color);
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
