clear;

% max_frame 11114
% min_frame 2
% all_ids [0, 1, 2, 3, 4, 5]
% max_frame 17424
% min_frame 11540
% all_ids [1, 3, 4, 2, 0]
% max_frame 23689
% min_frame 18041
% all_ids [0, 1, 2, 3, 4, 6, 7]
% max_frame 35057
% min_frame 24413
% all_ids [2, 3, 4, 0, 1]
% max_frame 46870
% min_frame 41829
% all_ids [0, 1, 2, 4, 5]
% max_frame 55116
% min_frame 50359
% all_ids [2, 4, 5, 0, 1]
% max_frame 63927
% min_frame 60289
% all_ids [0, 1, 2, 4, 5]


filename = 'seq06_crude.mat';
n_ids = 6;

load(filename)

n_frames = anno.n_frames;

new_positions = [];
new_collectives = {};
for i = 1:n_frames
    for j = 1:n_ids
        new_positions(j).data(i).gpoint = anno.positions{j}.data{i}.gpoint(:);
        if ~isempty(anno.interactions{i})
            for k = 1:n_ids
                if (j <= length(anno.interactions{i})) && (k <= length(anno.interactions{i}))
                    if (strcmp(anno.interactions{i}{j,k}, ''))
                        anno.interactions{i}{j,k} = [];
                    else
                        anno.interactions{i}{j,k} = translate_interaction(anno.interactions{i}{j,k});
                        if strcmp(anno.interactions{i}{j,k}, 'following')
                            anno.interactions{i}{k,j} = 'being followed';
                        end
                    end
                end
            end
        end
    end

    if length(anno.collective_behaviour{i}) == 1
        new_collectives{i} = [];
    else
        new_collectives{i} = translate_collective(anno.collective_behaviour{i});
    end
end

anno.positions = new_positions;
save('seq06.mat', 'anno');
