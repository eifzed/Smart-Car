import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np


def fuzzy_RCAS():
    position = ctrl.Antecedent(np.arange(-45, 45, 1), 'position')
    distance = ctrl.Antecedent(np.arange(0, 1000, 1), 'distance')
    speed_dif = ctrl.Antecedent(np.arange(-150, 0, 1), 'speed_dif')

    brake = ctrl.Consequent(np.arange(0, 1.2, 0.01), 'brake')
    steer = ctrl.Consequent(np.arange(-30, 30, 1), 'steer')

    # input
    distance['close'] = fuzz.trapmf(distance.universe, [0, 0, 140, 150])
    distance['medium'] = fuzz.trapmf(distance.universe, [140, 150, 200, 230])
    distance['far'] = fuzz.trapmf(distance.universe, [200, 230, 1000, 1000])


    speed_dif['big'] = fuzz.trapmf(speed_dif.universe, [-150, -150, -70, -50])
    speed_dif['medium'] = fuzz.trapmf(speed_dif.universe, [-60, -50, -30, -20])
    speed_dif['small'] = fuzz.trapmf(speed_dif.universe, [-30, -20, 0, 0])

    position['right'] = fuzz.trapmf(position.universe, [-45, -45, -7, -4])
    position['center'] = fuzz.trapmf(position.universe, [-7, -4, 4, 7])
    position['left'] = fuzz.trapmf(position.universe, [4, 7, 45, 45])

    # output
    steer['big_left'] = fuzz.trapmf(steer.universe, [-30, -30, -25, -20])
    steer['left'] = fuzz.trapmf(steer.universe, [-25, -20, -15, -5])
    steer['straight'] = fuzz.trapmf(steer.universe, [-10, -5, 5, 10])
    steer['right'] = fuzz.trapmf(steer.universe, [5, 15, 20, 25])

    brake['none'] = fuzz.trapmf(brake.universe, [0, 0, 0.015, 0.03])
    brake['soft'] = fuzz.trapmf(brake.universe, [0.015, 0.06, 0.3, 0.4])
    brake['hard'] = fuzz.trapmf(brake.universe, [0.35, 0.7, 0.85, 1])
    brake['very_hard'] = fuzz.trapmf(brake.universe, [0.85, 1, 1.2, 1.2])

    # Rules for LKAS

    rule1 = ctrl.Rule(distance['close'] & speed_dif['small'], (brake['hard'], steer['straight']))
    rule2 = ctrl.Rule(distance['close'] & speed_dif['medium'], (brake['very_hard'], steer['straight']))
    rule3 = ctrl.Rule(distance['close'] & speed_dif['big'], (brake['very_hard'], steer['big_left']))
    rule4 = ctrl.Rule(distance['medium'] & speed_dif['small'] & position['left'], (brake['none'], steer['right']))
    rule5 = ctrl.Rule(distance['medium'] & speed_dif['small'] & position['center'], (brake['none'], steer['straight']))
    rule6 = ctrl.Rule(distance['medium'] & speed_dif['small'] & position['right'], (brake['none'], steer['left']))
    rule7 = ctrl.Rule(distance['medium'] & speed_dif['medium'] & position['left'], (brake['soft'], steer['straight']))
    rule8 = ctrl.Rule(distance['medium'] & speed_dif['medium'] & position['center'], (brake['soft'], steer['straight']))
    rule9 = ctrl.Rule(distance['medium'] & speed_dif['medium'] & position['right'], (brake['soft'], steer['straight']))
    rule10 = ctrl.Rule(distance['medium'] & speed_dif['big'] & position['left'], (brake['hard'], steer['right']))
    rule11 = ctrl.Rule(distance['medium'] & speed_dif['big'] & position['center'], (brake['hard'], steer['straight']))
    rule12 = ctrl.Rule(distance['medium'] & speed_dif['big'] & position['right'], (brake['hard'], steer['left']))
    rule13 = ctrl.Rule(distance['far'] & speed_dif['small'] & position['left'], (brake['none'], steer['right']))
    rule14 = ctrl.Rule(distance['far'] & speed_dif['small'] & position['center'], (brake['none'], steer['straight']))
    rule15 = ctrl.Rule(distance['far'] & speed_dif['small'] & position['right'], (brake['none'], steer['left']))
    rule16 = ctrl.Rule(distance['far'] & speed_dif['medium'] & position['left'], (brake['soft'], steer['right']))
    rule17 = ctrl.Rule(distance['far'] & speed_dif['medium'] & position['center'], (brake['soft'], steer['straight']))
    rule18 = ctrl.Rule(distance['far'] & speed_dif['medium'] & position['right'], (brake['soft'], steer['left']))
    rule19 = ctrl.Rule(distance['far'] & speed_dif['big'] & position['left'], (brake['soft'], steer['right']))
    rule20 = ctrl.Rule(distance['far'] & speed_dif['big'] & position['center'], (brake['soft'], steer['straight']))
    rule21 = ctrl.Rule(distance['far'] & speed_dif['big'] & position['right'], (brake['soft'], steer['left']))

    fuzzy_RCAS = ctrl.ControlSystem([rule1, rule2, rule3, rule4,
                                     rule5, rule6, rule7, rule8,
                                     rule9, rule10, rule11, rule12,
                                     rule13, rule14, rule15, rule16,
                                     rule17, rule18, rule19, rule20,
                                     rule21])

    return ctrl.ControlSystemSimulation(fuzzy_RCAS)

fuzzy_RCAS()