function [new_interaction] = translate_interaction(interaction)


if strcmp(interaction, 'standing_pair')
    new_interaction = 'standing group';
elseif strcmp(interaction, 'approaching')
    new_interaction = 'approaching';
elseif strcmp(interaction, 'walking_together')
    new_interaction = 'walking group';
elseif strcmp(interaction, 'splitting')
    new_interaction = 'dismissal';
elseif strcmp(interaction, 'following')
    new_interaction = 'following';
elseif strcmp(interaction, 'being followed')
    new_interaction = 'being followed';
else
    warning('Did not found a good translate value for interaction.');
    disp(interaction);
    new_interaction = '';
end