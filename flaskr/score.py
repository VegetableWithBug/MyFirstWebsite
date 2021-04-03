import os
from math import sqrt,pow

#计算网扩值
def expend(x,wx,y):
    return 100*((1-pow(10,wx-x))/(1-pow(10,wx-y))-0.4)
#通用分数计算函数1
def score_one(weightScore, currentValue, level_down):
    score=weightScore
    if(currentValue>up):
        score=weightScore-pow(2,int((currentValue-up)/level_up))
        if(score<0):
            return 0
    return score
#通用分数计算函数2
def score_two(weightScore, currentValue, up, down, level_up, level_down):
    score=weightScore
    if(currentValue>up):
        score=weightScore-pow(2,int((currentValue-up)/level_up))
    elif(currentValue<down):
        score=weightScore-pow(2,int((down-currentValue)/level_down))
    if(score<0):
        return 0
    return score
#计算密度得分
def get_density_score(kk,cc,mm,yy,field_density):
    weight=field_density/4
    S_Dc_c = score_two(weight, cc, 0.9, 0.85, 0.02, 0.015)
    S_Dm_m = score_two(weight, mm, 0.9, 0.85, 0.02, 0.015)
    S_Dy_y = score_two(weight, yy, 0.9, 0.8, 0.02, 0.015)
    S_Dk_k = score_two(weight, kk, 1.1, 1.0, 0.03, 0.02)
    return (S_Dc_c + S_Dm_m + S_Dy_y + S_Dk_k)
#计算扩展值得分
def get_expend_score(cyan_expend,magenta_expend,yellow_expend,black_expend,four_expend):
    weight=four_expend/4
    S_F40=score_two(weight, cyan_expend, 22, 14, 2, 2)+score_two(weight, magenta_expend, 22, 14, 2, 2)+score_two(weight, yellow_expend, 22, 14, 2, 2)+score_two(weight, black_expend, 22, 14, 2, 2)
    return S_F40
#计算中间值得分
def get_middle_score(middle_expend,middle_expend_s):
    return score_one(middle_expend_s, middle_expend - 3, 1)
#计算报头密度得分
def get_header_density_score(tm,ty,header_magenta,header_yellow,header_density_difference):
    dtD = sqrt(pow(tm-header_magenta,2)+pow(ty-header_yellow),2)
    return score_one(header_density_difference, dtD - 0.1, 0.01)
#计算色差得分
def get_difference_score(cyan_difference,magenta_difference,yellow_difference,black_difference,gray_banlance_s):
    weight=gray_banlance_s/4
    return score_one(weight,abs(cyan_difference)-3,1)+score_one(weight,abs(magenta_difference)-5,1)+score_one(weight,abs(yellow_difference)-4,1)+score_one(weight,abs(black_difference)-3,1)
#计算灰平衡彩度差得分
def get_gray_score(gray_banlance,gray_banlance_s):
    return score_one(gray_banlance_s,gray_banlance-3,1)
#计算报头色度得分
def get_header_difference_score(header_difference,header_difference_s):
    return score_one(header_difference_s,header_difference,1.5)