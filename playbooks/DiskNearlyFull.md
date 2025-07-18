# DiskNearlyFull

This alert is triggered when a disk is over 80% full. We use this alert
across all monitored machines. Diagnosis and resolution is likely to differ
on a case-by-case basis.

The alert will mention the hostname and the mountpoint of the drive in
question.

## wpia-gpu-02

The GPU nodes, in particular GPU02, often end up accumulating lots of software
and data from its users which they don't always clean up and which, if left
unchecked, grows endlessly.

The following command will list all directories in the `/home` directory and
sort them by descending size:

```sh
sudo du -x -d 1 -h /home | sort -hr
```

If a particular user stands out in this list, you can contact them asking them
to remove any old data or software they may have lying around.

In addition to the root drive (which is "only" 400GB), the machine is equipped
with a very large drive mounted under `/data`. Users should be encouraged to
move any voluminous data to that drive.

The first time they need access to the `/data` drive, you can create a new
folder for them using the following command, replacing all instances of
`<USER>` with their username on that machine (which may not be the same as
their DIDE or IC username):

```sh
sudo install -d -o <USER> -g <USER> /data/<USER>
```

## `/boot` partition

After a kernel upgrade, the `/boot` partition may grow in size if the old
kernels aren't pruned. While Ubuntu should be handling automatically,
occasionally this does not seem to work as expected and old kernels can
accumulate.

Apt will avoid uninstalling the kernel that is currently booted: rebooting the
machine into the latest installed kernel followed by an `apt autoremove` can be
used to prune these kernel versions.

## Network and Pseudo filesystems

The metrics and alert are configured to ignore network and pseudo file system
types, including cifs (aka Windows network drives), procfs, sysfs, etc. In the
future it may be necessary to exclude additional file system types if new ones
crop up. This can be done most easily by modifying the alert definition.
