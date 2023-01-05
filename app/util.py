def table(rows: 'Sequence[Sequence]', printme=True, space=2) -> 'Sequence[Sequence[str]]':
    "format list of tuples into a table"
    if not rows:
        return rows
    ncols = max(map(len, rows))
    assert all(len(row) == ncols for row in rows) # or else column max width calc will fail below
    str_rows = [tuple(map(str, row)) for row in rows]
    cell_widths = [tuple(map(len, row)) for row in str_rows]
    col_widths = tuple(map(max, zip(*cell_widths)))
    padded = [
        tuple(cell.ljust(width + space) for cell, width in zip(row, col_widths))
        for row in str_rows
    ]
    if printme:
        spacer = ' ' * space
        for row in padded:
            print(spacer.join(row))
    return padded

class UserFacingError(Exception):
    def __init__(self, *args, response_code=500, **kwargs):
        self.response_code = response_code
        super().__init__(*args, **kwargs)
