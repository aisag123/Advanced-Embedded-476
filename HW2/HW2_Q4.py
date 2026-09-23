def series(R1, R2):
    R3 = R1 + R2
    return(R3)

def parallel(R1, R2):
    R3 = 1 / (1/R1 + 1/R2)
    return(R3)

R_left_lower = series(200, 150)
R_left = parallel(75, R_left_lower)
R_right_lower = parallel(250, 300)
R_right_mid = series(50, R_right_lower)
R_right = parallel(150, R_right_mid)
R_top = series(R_left, R_right)
rab = parallel(R_top, 350)

print(rab)
