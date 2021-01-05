import skfuzzy as fuzz
from skfuzzy import control as ctrl

def fuzzy_fusion():
    dist_cam = ctrl.Antecedent(np.arange(0, 320, 1), 'dist_cam')
    offset_center = ctrl.Antecedent(np.arange(0, 320, 1), 'offset_center')
    ult_weight = ctrl.Consequent(np.arange(0, 1, 0.01), 'ult_weight')

    # input
    offset_center['small'] = fuzz.trapmf(offset_center.universe, [0, 0, 150, 170])
    offset_center['big'] = fuzz.trapmf(offset_center.universe, [150, 170, 320, 320])

    dist_cam['small'] = fuzz.trapmf(dist_cam.universe, [0, 0, 110, 140])
    dist_cam['medium'] = fuzz.trapmf(dist_cam.universe, [110, 140, 170, 200])
    dist_cam['big'] = fuzz.trapmf(dist_cam.universe, [180, 200, 320, 320])

    # output
    ult_weight['small'] = fuzz.trapmf(ult_weight.universe, [0, 0, 0.3, 0.4])
    ult_weight['medium'] = fuzz.trapmf(ult_weight.universe, [0.3, 0.4, 0.5, 0.6])
    ult_weight['big'] = fuzz.trapmf(ult_weight.universe, [0.5, 0.6, 1, 1])

    # Rules for LKAS
    rule1 = ctrl.Rule(offset_center['small'] & dist_cam['small'], (ult_weight['big']))
    rule2 = ctrl.Rule(offset_center['big'] & dist_cam['medium'], (ult_weight['small']))
    rule3 = ctrl.Rule(offset_center['small'] & dist_cam['big'], (ult_weight['medium']))
    rule4 = ctrl.Rule(offset_center['big'] & dist_cam['small'], (ult_weight['medium']))
    rule5 = ctrl.Rule(offset_center['small'] & dist_cam['medium'], (ult_weight['big']))
    rule6 = ctrl.Rule(offset_center['big'] & dist_cam['big'], (ult_weight['small']))


    fusion = ctrl.ControlSystem([rule1, rule2, rule3,
                                 rule4, rule5, rule6])

    return ctrl.ControlSystemSimulation(fusion)


if __name__ == '__main__':
    def distant_fusion(dist_ult, dist_cam, offset_center):
        fusion.input['offset_center'] = offset_center
        fusion.input['dist_cam'] = dist_cam
        fusion.compute()
        ult_weight = fusion.output['ult_weight']
        cam_weight = 1 - ult_weight
        dist_fusion = dist_ult*ult_weight + dist_cam*cam_weight
        return dist_fusion

    dist_cam_list = [310,270,314,250,290,300,274,275,270,238,235,221.4242166,220,220,220,192.2546687,175,185,183.243863,153.0833782,165.1435249,159.1097348,131.5925153,140.8588334,125,120,121.2419759,105.584052,98.22738128,114.4536903,96.77752098,89.73120436,96.39816459,69.98782656,68.259745,70.15358222,50.60500547,51.52156568,52.06825231]
    offset_center_list = [77.1,225,155.41,74.51,226.23,213.6,64.91,228.18,222.62,56.76,224.44,255.79,48.26,242.8,220.78,43.44,212.89,206.15,35.15,249.97,258.69,22.61,217.88,249.27,9.1,224.36,205.9,40.88,195,198.3,57.56,204.09,221.5,113.83,180.47,242.7,160.18,228.71,218.8]
    dist_ult_list = [290,320,318,266.68,320,300,247.04,182.97,256,230,290,270,210.17,250,230,192,184.85,180,172,175,175,153.72,158.41,155,130,130,133.3,110,111,110,90,91,92,70,70,70,51,50,50]
    print(len(dist_ult_list), len(dist_cam_list), len(offset_center_list))
    fusion = start_fuzzy()

    for i in range(len(dist_cam_list)):
        dist_cam = dist_cam_list[i]
        offset_center = offset_center_list[i]
        dist_ult = dist_ult_list[i]

        print(distant_fusion(dist_ult, dist_cam, offset_center))


