close all
clear
clc

while 1
    [baseName, folder] = uigetfile('.hdf');
    if baseName == 0
        break
    end
    fullFileName = fullfile(folder, baseName);
    hdf = h5read(fullFileName,'/dataGroup/dataTable');
    data = hdf.out;
    figure(1)
    plot(data(:,1));
    pause()
end