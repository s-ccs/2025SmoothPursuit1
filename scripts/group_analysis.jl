using PyMNE
using Unfold
using DataFrames
using CSV
using UnfoldMakie, CairoMakie
#using PyCall
#----
# load raw dat

subj = "010"

raw_fname = "/scratch/data/2025SmoothPursuit1/derivs/sub-$(subj)/ses-001/eeg/sub-$(subj)_ses-001_task-sp1_run-1_proc-clean_raw.fif"
raw = PyMNE.io.Raw(raw_fname, preload=true)
sfreq = pyconvert(Int, raw.info["sfreq"])
raw.filter(l_freq=0.3, h_freq=20)
#raw.notch_filter([50])
eye_data = raw.get_data(picks="eyegaze")
x_data = eye_data[[0,2]].mean(axis=0)
y_data = eye_data[[1,3]].mean(axis=0)
channel = "POz"

## generate the event table
# get things into julia
e, e_id = PyMNE.events_from_annotations(raw, regexp="\\d-trigger=15 Image centred.*")
f, f_id = PyMNE.events_from_annotations(raw, regexp=".*fixation.*")
e_id = [string(ee_id) for ee_id in e_id]
e = pyconvert(Array, e)
f_id = [string(ff_id) for ff_id in f_id]
f = pyconvert(Array, f)
e_id = e_id[e[:,3]] # MNE inexplicably does not sort the e_ids; this straightens them out
f_id = f_id[f[:,3]]

# build the table
evts = DataFrame(stimulus=[], condition=[], latency=Int[], trig_latency=[], follow=[],
                 direction=[])
for (ee, ee_id) in zip(e, e_id)
    condition = occursin("face", ee_id) == true ? "face" : "egg"
    direction = occursin("left", ee_id) == true ? "left" : "right"
    follow = occursin("fix", ee_id) == true ? "fix" : "sp"
    stimulus = match(r"image=(.*).png", ee_id).captures[1]
    # #fix_idx = f[argmin(abs.(f[:,1] .- ee)), 1]
    dists = convert.(Float64, f[:,1]) .- ee
    dists[dists.<0] .= Inf
    dist_min_idx = argmin(dists)
    fix_idx = f[dist_min_idx]
    new_row = DataFrame(stimulus=stimulus, condition=condition, latency=fix_idx, 
                        trig_latency=ee, follow=follow, direction=direction)
    append!(evts, new_row)
end


# epoching
data = raw.get_data(picks=channel, units="uV")
data = pyconvert(Array, data)
data_epochs, times = Unfold.epoch(data = data, tbl = evts, τ = (-0.4, 1.), sfreq = sfreq)

# model
form = @formula 0 ~ 1 + condition + follow + direction
m = fit(UnfoldModel, form, evts, data_epochs, times)

# plot
eff = effects(Dict(:follow => ["fix", "sp"]), m)
fig = Figure(;size=(1440, 1440), title="Fix vs SP")
plot_erp!(fig, eff; mapping = (; color = :follow,))
display(fig)

eff = effects(Dict(:follow => ["fix", "sp"], :condition => ["face", "egg"]), m)
fig = Figure(;size=(2860, 1440), title="face vs egg, fix vs sp")
#plot_erp!(fig, eff; visual = (; linewidth = 8), mapping = (; color = :stimulus, col = :follow), axis = (; xticklabelsize=30, yticklabelsize=30, titlesize=35, xlabelsize=35, ylabelsize=35), legend = (; titlesize=35, labelsize=30) )
plot_erp!(fig, eff; mapping = (; color = :follow, col = :condition))
display(fig)

# eff = effects(Dict(:follow => ["fix", "follow"], :hit_ratio => .7:.1:1., :stim_type => ["face", "egg"]), m)
# fig = Figure(;size=(1920, 1200))
# plot_erp!(fig, eff; mapping = (; color = :stim_type, col = :hit_ratio, row = :follow))

eff = effects(Dict(:condition => ["face", "egg"]), m)
fig = Figure(;size=(1440, 1440), title="face vs egg")
plot_erp!(fig, eff; mapping = (; color = :condition))
display(fig)

eff = effects(Dict(:direction => ["left", "right"]), m)
fig = Figure(;size=(1440, 1440), title="left vs right")
plot_erp!(fig, eff; mapping = (; color = :direction))
display(fig)

# model topography 
# epoching
raw.interpolate_bads()
data = raw.get_data(picks="eeg", units="uV")
data = pyconvert(Array, data)
data_epochs, times = Unfold.epoch(data = data, tbl = evts, τ = (-0.4, 1.), sfreq = sfreq)
form = @formula 0 ~ 1 + condition + follow + direction
m = fit(UnfoldModel, form, evts, data_epochs, times)
eff = effects(Dict(:follow => ["fix", "sp"]), m)
eff_crop = filter(row -> row.time <= .2 && row.time >= -.1, eff)
# get channel positions
layout = pyimport("mne.channels.layout")
pos = layout._find_topomap_coords(raw.info, "eeg")
pos = pyconvert(Array, pos)
vpos = [[pos[i,1], pos[i,2]] for i in axes(pos,1)]
plot_topoplotseries(eff_crop, positions=vpos, bin_num=12, nrows=2)

eff = effects(Dict(:follow => ["fix", "sp"]), m)
fig = Figure(;size=(2560, 1200))
plot_topoplotseries!(fig, eff, positions=vpos, bin_num=15, mapping=(; row=:follow))
display(fig)
