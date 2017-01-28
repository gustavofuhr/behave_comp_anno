function [trans_behav] = translate_collective(behav)

if strcmp(behav, 'Dismissal')
    trans_behav = 'dismissal';
elseif strcmp(behav, 'Gathering')
    trans_behav = 'approaching';
elseif strcmp(behav, 'Talking')
    trans_behav = 'standing group';
elseif strcmp(behav, 'Walking')
    trans_behav = 'walking group';
elseif strcmp(behav, 'Chasing')
    trans_behav = 'following';
else
    error('no identified collective behaviour!');
end