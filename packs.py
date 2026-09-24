'''Finds clusters (concentrations) of points - their centers, ranges
'''
def calc_avg(ps:list[int]) -> float:
    return sum(ps)/len(ps)


def calc_diffs(ps:list[int], absolute:bool=False) -> list[int]:
    diffs_num = max(len(ps) - 1, 0)
    if diffs_num == 0:
        return []
    else:
        diffs:list[int] = [0] * diffs_num
        i = 0
        while i != len(ps) - 1:
            diff = ps[i + 1] - ps[i]
            if absolute: diff = abs(diff)
            diffs[i] = diff
            i += 1
        print('DIFFR', diffs) #, calc_avg(diffs), calc_rmsd(diffs, normalize_with_iqr=False))
        return diffs


class RangeBounds(list): ...
class Isolines(list): ...


def sign(x):
    return -1 if x < 0 else 1


def calc_ratio(x:int|float, y:int|float) -> float:
    abs_x = abs(x)
    abs_y = abs(y)
    res_sign = sign(x) * sign(y)
    if abs_x == 0 and abs_y == 0:
        return float('nan')
    elif abs_x > abs_y:
        if abs_y == 0:
            if res_sign < 0:
                return float('-inf')
            else:
                return float('inf')
        else:
            return x / y
    elif abs_x < abs_y:
        if abs_x == 0:
            if res_sign < 0:
                return float('-inf')
            else:
                return float('inf')
        else:
            return y / x
    else: #if abs_x == abs_y:
        if abs_x == 0:
            return float('nan')
        else:
            return res_sign


def approximate_by_rectangles(ps:list[int], tolerance:float=1.5) -> tuple[RangeBounds,Isolines]:
    def new_rect_is_needed(slice, p):
        # new rect if current point p is too high/low comparing to min/max of current slice
        if slice:
            slice_max = max(slice)
            slice_min = min(slice)
            return calc_ratio(p, slice_max) > tolerance or calc_ratio(p, slice_min) > tolerance
        raise ValueError('slice is empty')
    res_ps:Isolines = Isolines()
    res_ranges:RangeBounds = RangeBounds()
    slice = []
    for p in ps:
        if not slice:
            slice.append(p)
        else:
            if new_rect_is_needed(slice, p):
                slice_avg = calc_avg(slice)
                res_ps.extend(len(slice) * [slice_avg])
                slice = [p]
            else:
                slice.append(p)
    if slice:
        slice_avg = calc_avg(slice)
        res_ps.extend(len(slice) * [slice_avg])
    pr = None
    for i, r in enumerate(res_ps):
        if i == 0:
            res_ranges.append(i)
        elif i != 0 and pr != r:
            res_ranges.append(i)
        pr = r
    print('APPRX', res_ps, res_ranges)
    assert len(res_ps) >= len(res_ranges)
    return (res_ranges, res_ps)


def find_clusters_centers(
        *,
        ranges:RangeBounds,
        isovalues:Isolines,
        ratio:float=2,
        nesting:int=0) -> list[tuple[int,int]]:
    '''Finds high concentrations of points based on the approximation of the distance
    between neighboring points by rectangles. The input from approximation is ranges and isovalues
    '''
    prev_isovalue = None
    res = []
    max_irange = len(ranges) - 1
    for irange in range(0, max_irange + 1):
        isovalue = isovalues[ranges[irange]]
        if prev_isovalue is not None:
            if isovalue > prev_isovalue and calc_ratio(isovalue, prev_isovalue) >= ratio:
                # left___/‾‾
                right = ranges[irange]
                left = ranges[max(irange - 1, 0)]
            elif isovalue < prev_isovalue and calc_ratio(prev_isovalue, isovalue) >= ratio:
                # ‾‾\___right
                left = ranges[irange]
                right = ranges[min(irange + 1, max_irange)]
            else:
                prev_isovalue = isovalue
                continue
            if right == left:
                right += 1
            left += nesting
            right += nesting
            if not res or res[-1] != (left, right):
                # ‾‾\___, ___/‾‾ such cases would be reported twice w/o this "if" checking that
                # if was not reported in `res` in the previous time:
                res.append((left, right))
        prev_isovalue = isovalue
    return res


def calc_clusters(ps:list[int]):
    diffs = calc_diffs(ps)
    ranges, isovalues = approximate_by_rectangles(diffs, tolerance=2)
    clusters = find_clusters_centers(ranges=ranges, isovalues=isovalues, nesting=0)
    return clusters


#ps = [1,7,9,10,11,13,15,16,18,19,25,30,34,36,37,38,39,40,42,43,45,46,49,52,58]
ps = [1,100,200]
# ps = [1,2,10,20,30,40,50,60,70,80,90,100,101]
# ps = [1,2,1,1,1,10,20,30,40,50,60,70,80,90,100,101]
print('INPUT', ps)
clusters = calc_clusters(ps)
print('CLUST', clusters)
