// Configurable Parameters:

// Animation duration in seconds.
const float duration_seconds = 0.15;

// FIN

bool box_contains(const vec2 p, const vec4 bb) {
  return bb.x < p.x
    && p.x < bb.z
    && bb.y < p.y
    && p.y < bb.w;
}

vec4 bb(const vec4 rect) {
  return vec4(rect.xy - vec2(0, rect.w), rect.xy + vec2(rect.z, 0));
}

vec2 left_top(const vec4 bb) {
  return bb.xy;
}

vec2 left_bottom(const vec4 bb) {
  return bb.xw;
}

vec2 right_top(const vec4 bb) {
  return bb.zy;
}

vec2 right_bottom(const vec4 bb) {
  return bb.zw;
}

vec4 alpha_blend(const vec4 x, const vec4 y) {
  const float a = mix(x.a, 1, y.a);
  const vec3 rgb = mix(y.a * y.rgb, x.rgb, x.a) / a;
  return vec4(rgb, a);
}

bool quad_contains(
  const vec2 p,
  const vec2 a,
  const vec2 b,
  const vec2 c,
  const vec2 d
) {
  const vec2 v0 = b - a;
  const vec2 v1 = c - b;
  const vec2 v2 = d - c;
  const vec2 v3 = a - d;

  const float d0 = determinant(mat2(p - a, v0));
  const float d1 = determinant(mat2(p - b, v1));
  const float d2 = determinant(mat2(p - c, v2));
  const float d3 = determinant(mat2(p - d, v3));

  const bool neg = d0 < 0 || d1 < 0 || d2 < 0 || d3 < 0;
  const bool pos = d0 > 0 || d1 > 0 || d2 > 0 || d3 > 0;

  return !(neg && pos);
}

const vec2 d = vec2(sqrt(2), -sqrt(2)) * 0.5;
const float speed = 1 / duration_seconds;

void mainImage(out vec4 frag_color, vec2 frag_coord) {
  const vec2 uv = frag_coord / iResolution.xy;
  const vec4 color = texture2D(iChannel0, uv);
  frag_color = color;

  if (iPreviousCursor.z == 0 || iPreviousCursor.w == 0) {
    return;
  }

  const vec4 curr = bb(iCurrentCursor);
  const vec4 prev = bb(iPreviousCursor);

  const vec2 curr_center = mix(curr.xy, curr.zw, 0.5);
  const vec2 prev_center = mix(prev.xy, prev.zw, 0.5);
  const vec2 diff = curr_center - prev_center;

  if (diff == vec2(0, 0)) {
    return; // diff can't be normalized
  }

  const float t0 = min((iTime - iTimeCursorChange) * speed, 1);

  const vec2 dir = normalize(diff);
  const vec4 cos_theta = vec4(
    dot(dir, d.xx),
    dot(dir, d.xy),
    dot(dir, d.yy),
    dot(dir, d.yx)
  );
  const vec4 p = mix(vec4(0), vec4(1), (cos_theta + vec4(1)) * 0.5);
  const vec4 t = pow(vec4(t0), p);

  if (quad_contains(
    frag_coord,
    mix(left_top(prev), left_top(curr), t.x),
    mix(left_bottom(prev), left_bottom(curr), t.y),
    mix(right_bottom(prev), right_bottom(curr), t.z),
    mix(right_top(prev), right_top(curr), t.w)
  )) {
    frag_color = alpha_blend(iCurrentCursorColor, frag_color);
  }
  if (box_contains(frag_coord, curr)) {
    frag_color = color;
  }
}
