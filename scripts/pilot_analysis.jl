using Unfold
using UnfoldMakie,CairoMakie
using PyMNE
using DataFrames
using CSV
#using PyCall
#----
# load raw data

subj = "997"

raw_fname = "/home/hanna/scratch/2025SmoothPursuit1_data/derivs/sub-$(subj)/ses-001/eeg/sub-$(subj)_ses-001_task-2025SmoothPursuit1_proc-clean_raw.fif"
raw = PyMNE.io.Raw(raw_fname, preload=true)
sfreq = pyconvert(Int, raw.info["sfreq"])
raw.filter(l_freq=0.3, h_freq=20)
#raw.notch_filter([50])
eye_data = raw.get_data(picks="eyegaze")
x_data = eye_data[[0,2]].mean(axis=0)
y_data = eye_data[[1,3]].mean(axis=0)

if subj == "998"
    montage = PyMNE.channels.read_dig_fif("/home/hanna/NA-271_ASA.fif")
    raw.set_montage(montage)
    channel = "Z12"
else
    channel = "O1"
end

#---
# get the table
df_csv = DataFrame(CSV.File("/home/hanna/scratch/2025SmoothPursuit1_data/sub-997/ses-001/beh/sub-997_ses-001_task-2025SmoothPursuit1_run-001_subject-997.csv", header=4))
# get rid of practice rounds
df_csv = df_csv[5:end, :]

## generate the event table
# get things into julia
e, e_id = PyMNE.events_from_annotations(raw, regexp="trigger=15 Image centred.*")
f, f_id = PyMNE.events_from_annotations(raw, regexp=".*fixation.*")
e_id = [string(ee_id) for ee_id in e_id]
e = pyconvert(Array, e)
f_id = [string(ff_id) for ff_id in f_id]
f = pyconvert(Array, f)
e_id = e_id[e[:,3]] # MNE inexplicably does not sort the e_ids; this straightens them out
f_id = f_id[f[:,3]]
# # build the table
# evts = DataFrame(follow=[], left=[], hit_ratio=Float64[], latency=Int[], stim_type=[])
# for (ee, ee_id, df_csv_row) in zip(e, e_id, eachrow(df_csv))
#     if !occursin(df_csv_row[3], ee_id)
#         error("csv says $(df_csv_row[3]) and raw says $ee_id\n")
#     end
#     follow = df_csv_row[1] == false ? "fix" : "follow"
#     left = df_csv_row[2] == false ? "right" : "left"
#     hit_ratio = df_csv_row[4]
#     stim_type = occursin("face", df_csv_row[3]) == true ? "face" : "egg"
#     new_row = DataFrame(follow=follow, left=left, hit_ratio=hit_ratio, latency=ee, stim_type=stim_type)
#     append!(evts, new_row)
# end
# build the table
evts = DataFrame(Stimulus=[], latency=Int[], trig_latency=[], follow=[],
                 direction=[])
for (ee, ee_id) in zip(e, e_id)
    stim_type = occursin("face", ee_id) == true ? "Face" : "Egg"
    #fix_idx = f[argmin(abs.(f[:,1] .- ee)), 1]
    dists = convert.(Float64, f[:,1]) .- ee
    dists[dists.<0] .= Inf
    dist_min_idx = argmin(dists)
    fix_idx = f[dist_min_idx]
    x_val = pyconvert(Float64, x_data[fix_idx])
    y_val = pyconvert(Float64, y_data[fix_idx])
    if dists[dist_min_idx] > 300 || abs(x_val) > 200 || abs(y_val+150) > 50
        continue
    end
    x_val_tau = pyconvert(Float64, x_data[fix_idx+500])
    follow = abs(x_val_tau - x_val)
    if abs(x_val_tau - x_val) > 50
        follow = "SmoothPursuit"
    else
        follow = "Fixation"
    end
    x_val_tau = pyconvert(Float64, x_data[fix_idx-500])
    if x_val_tau > x_val
        direction = "left"
    else
        direction = "right"
    end
    new_row = DataFrame(Stimulus=stim_type, latency=fix_idx, 
                        trig_latency=ee, follow=follow,
                        direction=direction)
    append!(evts, new_row)
end


# epoching
data = raw.get_data(picks=channel, units="uV")
data = pyconvert(Array, data)
data_epochs, times = Unfold.epoch(data = data, tbl = evts, τ = (-0.4, 1.), sfreq = sfreq)

# model
form = @formula 0 ~ 1 + Stimulus + follow + direction
m = fit(UnfoldModel, form, evts, data_epochs, times)

# plot
eff = effects(Dict(:follow => ["Fixation", "SmoothPursuit"]), m)
plot_erp(eff; mapping = (; color = :follow,))

eff = effects(Dict(:follow => ["Fixation", "SmoothPursuit"], :Stimulus => ["Face", "Egg"]), m)
fig = Figure(;size=(2860, 1440))
plot_erp!(fig, eff; visual = (; linewidth = 8), mapping = (; color = :Stimulus, col = :follow), axis = (; xticklabelsize=30, yticklabelsize=30, titlesize=35, xlabelsize=35, ylabelsize=35), legend = (; titlesize=35, labelsize=30) )

# eff = effects(Dict(:follow => ["fix", "follow"], :hit_ratio => .7:.1:1., :stim_type => ["face", "egg"]), m)
# fig = Figure(;size=(1920, 1200))
# plot_erp!(fig, eff; mapping = (; color = :stim_type, col = :hit_ratio, row = :follow))

eff = effects(Dict(:stim_type => ["face", "egg"]), m)
plot_erp(eff; mapping = (; color = :stim_type))

eff = effects(Dict(:direction => ["left", "right"]), m)
plot_erp(eff; mapping = (; color = :direction))

# model topography 
# epoching
data = raw.get_data(picks="eeg", units="uV")
data = pyconvert(Array, data)
data_epochs, times = Unfold.epoch(data = data, tbl = evts, τ = (-0.4, 1.), sfreq = sfreq)
form = @formula 0 ~ 1 + stim_type + follow + direction
m = fit(UnfoldModel, form, evts, data_epochs, times)
eff = effects(Dict(:follow => ["fix", "follow"]), m)
eff_crop = filter(row -> row.time <= .2 && row.time >= -.1, eff)
# get channel positions
layout = pyimport("mne.channels.layout")
pos = layout._find_topomap_coords(raw.info, "eeg")
pos = pyconvert(Array, pos)
vpos = [[pos[i,1], pos[i,2]] for i in axes(pos,1)]
plot_topoplotseries(eff_crop, positions=vpos, bin_num=12, nrows=2)

eff = effects(Dict(:direction => ["left", "right"], :follow => ["follow"]), m)
fig = Figure(;size=(2560, 1200))
plot_topoplotseries!(fig, eff, positions=vpos, bin_num=15, mapping=(; row=:direction))
