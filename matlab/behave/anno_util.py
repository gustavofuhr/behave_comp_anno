import numpy as np
import copy

def homog(pt):
    """
    Transform the point to homogeneous coordinates
    """
    return np.expand_dims(np.append(pt,1), axis=1)

def gpoint2image(H, pt):
    return get_groundpoint(np.linalg.inv(H), pt)

def get_groundpoint(H, pt):
    gp = H*homog(pt)

    # normalize back again the point
    gp = gp/gp[2]
    gp = np.squeeze(np.asarray(gp)) # need to convert to ndarray, the matrix mult makes it a np.matrix

    return gp[0:2]

def translate_interaction(interaction):
    interaction = interaction.strip().split(' ')[0]
    if interaction == 'InGroup':
        return 'standing_pair'
    elif interaction == 'Approach':
        return 'approaching'
    elif interaction == 'WalkTogether':
        return 'walking_together'
    elif interaction == 'Split':
        return 'splitting'
    elif interaction == 'Following':
        return 'following'
    elif interaction == 'RunTogether':
        return 'walking_together'
    # TODO: threat ignore interaction
    elif interaction == 'Ignore':
        return ''
    elif interaction == 'Chase':
        return 'following'
    elif interaction == 'Fight':
        return ''
    elif interaction == 'Meet':
        return 'meet?'
    else:
        raise Exception('Interaction '+interaction+' not understood.')


def abbreviate_interaction(interaction):
    if interaction == 'standing_pair':
        return 'SP'
    elif interaction == 'approaching':
        return 'Ap'
    elif interaction == 'walking_together':
        return 'WT'
    elif interaction == 'splitting':
        return 'S'
    elif interaction == 'following':
        return 'F'
    elif interaction == 'being_followed':
        raise Exception('should not exist')
    elif interaction == '':
        return 'I'
    else:
        return interaction


def add_interaction(interaction_matrix, sstart, send, interaction):
    if sstart in interaction_matrix:
        interaction_matrix[sstart][send] = copy.deepcopy(interaction)
    else:
        interaction_matrix[sstart] = {
            send: interaction
        }

    return interaction_matrix


def repeat_interaction(inter_frame, fstart, fend, interaction_matrix):
    for fr in range(fstart, fend+1):
        if fr not in inter_frame:
            inter_frame[fr] = copy.deepcopy(interaction_matrix)
        else:
            for t in interaction_matrix.keys():
                if t in inter_frame[fr]:
                    d = copy.deepcopy(inter_frame[fr][t])
                    d.update(interaction_matrix[t])
                    inter_frame[fr][t] = d
                else:
                    inter_frame[fr][t] = copy.deepcopy(interaction_matrix[t])

    return inter_frame