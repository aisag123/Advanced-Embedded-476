def series(R1, R2):
    R3 = R1 + R2
    return(R3)

def parallel(R1, R2):
    R3 = 1 / (1/R1 + 1/R2)
    return(R3)

Z_left_lower  = series(200j, 150)
Z_left        = parallel(75, Z_left_lower)
Z_right_lower = parallel(250, -300j)
Z_right_mid   = series(30j, Z_right_lower)
Z_right       = parallel(150j, Z_right_mid)
Z_top         = series(Z_left, Z_right)
zab           = parallel(Z_top, 350)

print(zab)

