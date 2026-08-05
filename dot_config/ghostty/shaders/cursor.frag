// Ghostty Master Shader — Silky Smooth Liquid Cursor Trail, Connected Reticle & Seamless Character Drop (Robust TUI / Pi Agent Support)

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

float dist_to_segment(vec2 P, vec2 A, vec2 B) {
  vec2 AB = B - A;
  float len_sq = dot(AB, AB);
  if (len_sq == 0.0) return length(P - A);
  float t_proj = clamp(dot(P - A, AB) / len_sq, 0.0, 1.0);
  vec2 projection = A + t_proj * AB;
  return length(P - projection);
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

  // Check if cursor exists (Robust TUI / Pi Agent support: works even if TUI app sets cursor alpha <= 0.1)
  bool is_focused = (iCurrentCursor.z > 0.0 || iPreviousCursor.z > 0.0);

  // Fallback cursor color for TUI apps
  vec4 active_cursor_color = iCurrentCursorColor;
  if (active_cursor_color.a < 0.1 || length(active_cursor_color.rgb) < 0.1) {
    active_cursor_color = vec4(0.85, 0.88, 0.82, 1.0);
  }

  const vec4 curr = bb(iCurrentCursor);
  const vec4 prev = bb(iPreviousCursor);

  const vec2 curr_center = mix(curr.xy, curr.zw, 0.5);
  const vec2 prev_center = mix(prev.xy, prev.zw, 0.5);
  const vec2 diff = curr_center - prev_center;

  // Detect focus loss / gain cursor shape transition (e.g. beam <-> hollow box)
  bool is_shape_change = (abs(iCurrentCursor.z - iPreviousCursor.z) > 2.0) || (abs(iCurrentCursor.w - iPreviousCursor.w) > 2.0);

  // Validate cursor movement range (ignore teleports / newlines / clears > 200px)
  bool is_valid_move = !is_shape_change && (length(diff) > 2.0) && (length(diff) < 200.0);

  float type_time = (iTimeCursorChange > 0.0) ? (iTime - iTimeCursorChange) : 1.0;
  vec2 render_uv = uv;
  vec2 anim_pos = frag_coord;

  // 1. Dynamic Character Drop & Scale-Down Entry Animation (Warping anim_pos & render_uv)
  if (is_focused && !is_shape_change && type_time > 0.0 && type_time < 0.22) {
    vec2 rel_pos = frag_coord - curr_center;
    float dist = length(rel_pos);
    if (dist < 32.0) {
      float anim_t = type_time / 0.22;
      float ease = 1.0 - pow(1.0 - anim_t, 3.0); // easeOutCubic
      float inv_t = 1.0 - ease;

      // Smooth radial weight transition to zero at 32px boundary
      float weight = smoothstep(32.0, 5.0, dist) * inv_t;

      float scale = 1.0 + 0.25 * weight;
      float drop_y = -5.0 * weight;

      anim_pos = curr_center + rel_pos / scale + vec2(0.0, drop_y);
      render_uv = anim_pos / iResolution.xy;
    }
  }

  const vec4 color = texture2D(iChannel0, render_uv);
  frag_color = color;

  // 2. Text Bloom / Glow (Only when window is focused)
  if (is_focused && bloom_strength > 0.0) {
    vec2 px = 1.5 / iResolution.xy;
    vec4 bloom_sum = texture2D(iChannel0, render_uv + vec2(-px.x, -px.y)) * 0.0625 +
                     texture2D(iChannel0, render_uv + vec2( 0.0,  -px.y)) * 0.125  +
                     texture2D(iChannel0, render_uv + vec2( px.x, -px.y)) * 0.0625 +
                     texture2D(iChannel0, render_uv + vec2(-px.x,   0.0)) * 0.125  +
                     texture2D(iChannel0, render_uv + vec2( 0.0,    0.0)) * 0.25   +
                     texture2D(iChannel0, render_uv + vec2( px.x,   0.0)) * 0.125  +
                     texture2D(iChannel0, render_uv + vec2(-px.x,  px.y)) * 0.0625 +
                     texture2D(iChannel0, render_uv + vec2( 0.0,   px.y)) * 0.125  +
                     texture2D(iChannel0, render_uv + vec2( px.x,  px.y)) * 0.0625;
    frag_color.rgb += bloom_sum.rgb * bloom_strength;
  }

  // 3. Animated Cursor Trailing Tail & Connected Bracket Reticle (Pi Agent / TUI Supported)
  if (is_focused) {

    // Connected Bracket Reticle Animation (锁定在 iPreviousCursor 刚印出的字符上，左右连通)
    if (is_valid_move && type_time > 0.0 && type_time < 0.18) {
      float drop_t = type_time / 0.18;
      float water_fade = pow(1.0 - drop_t, 2.0);

      // Force full cell width (~10px) for prev cell
      float cell_w = max(iCurrentCursor.z, 10.0);
      vec4 full_prev_box = vec4(prev_center.x - cell_w * 0.5, prev.y, prev_center.x + cell_w * 0.5, prev.w);

      // Expanding box around full cell box (0 to 4px outward)
      float expand = drop_t * 4.0;
      vec4 box = vec4(full_prev_box.x - expand, full_prev_box.y - expand, full_prev_box.z + expand, full_prev_box.w + expand);

      // Hard Bounding Box Guard: strictly inside box + 2px
      if (box_contains(anim_pos, vec4(box.x - 2.0, box.y - 2.0, box.z + 2.0, box.w + 2.0))) {
        float corner_len = 4.0; // Vertical leg length
        float thick = 1.0;      // 1px line thickness

        vec2 lt = anim_pos - left_top(box);
        vec2 lb = anim_pos - left_bottom(box);
        vec2 rt = anim_pos - right_top(box);
        vec2 rb = anim_pos - right_bottom(box);

        // Connected Top Bracket (Top horizontal bar + 2 vertical corner legs):
        bool is_top_bracket =
          (anim_pos.x >= box.x && anim_pos.x <= box.z && abs(anim_pos.y - box.w) <= thick) ||
          (lt.y <= 0.0 && lt.y >= -corner_len && abs(lt.x) <= thick) ||
          (rt.y <= 0.0 && rt.y >= -corner_len && abs(rt.x) <= thick);

        // Connected Bottom Bracket (Bottom horizontal bar + 2 vertical corner legs):
        bool is_bottom_bracket =
          (anim_pos.x >= box.x && anim_pos.x <= box.z && abs(anim_pos.y - box.y) <= thick) ||
          (lb.y >= 0.0 && lb.y <= corner_len && abs(lb.x) <= thick) ||
          (rb.y >= 0.0 && rb.y <= corner_len && abs(rb.x) <= thick);

        if (is_top_bracket || is_bottom_bracket) {
          frag_color.rgb += active_cursor_color.rgb * water_fade * 0.45;
        }
      }
    }

    // Liquid Cursor Trailing Animation (Perturbed seamlessly using anim_pos)
    if (is_valid_move) {
      const float progress = min((iTime - iTimeCursorChange) * speed, 1.0);

      if (progress < 1.0) {
        // High-order Quintic Ease-Out curve for ultra-silky fluid deceleration (0.52s)
        const float t = 1.0 - pow(1.0 - progress, 4.5);
        const float fade = pow(1.0 - progress, 1.5);

        vec3 trail_rgb = active_cursor_color.rgb;

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

        // Check if perturbed pixel position anim_pos is within the liquid hull
        bool in_trail = quad_contains(anim_pos, t_lt, t_lb, c_lb, c_lt) ||
                        quad_contains(anim_pos, t_lb, t_rb, c_rb, c_lb) ||
                        quad_contains(anim_pos, t_rb, t_rt, c_rt, c_rb) ||
                        quad_contains(anim_pos, t_rt, t_lt, c_lt, c_rt) ||
                        quad_contains(anim_pos, t_lt, t_lb, t_rb, t_rt);

        if (in_trail) {
          // Compute anti-aliased edge smoothing for liquid trail using anim_pos
          vec2 tail_center = mix(prev_center, curr_center, t);
          float dist_seg = dist_to_segment(anim_pos, tail_center, curr_center);
          float max_rad = max(iCurrentCursor.z, iCurrentCursor.w) * 0.5;
          float edge_aa = smoothstep(max_rad, max(0.0, max_rad - 2.0), dist_seg);

          // Trail opacity tuned to 70% max with smooth anti-aliased edges
          vec4 trail_color = vec4(trail_rgb, fade * 0.70 * mix(0.7, 1.0, edge_aa));
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
