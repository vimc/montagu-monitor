# DiskNearlyFull

This alert is triggered when a disk is over 80% full. We use this alert
across all monitored machines. Diagnosis and resolution is likely to differ
on a case-by-case basis.

The alert will mention the hostname and the mountpoint of the drive in
question.

## wpia-gpu-02

The GPU nodes, in particular GPU02, often end up accumulating lots of software
and data from its users in their home directories, which, if left unchecked,
grows endlessly.

The `/home` directory is mounted on its own 4TB drive. For historical reasons,
`/home/old-data` is bind-mounted onto `/data` and users may have data in there
as well (we will get rid of this eventually). `/home` and `/data` are the same
disk, but two distinct alerts will fire each time the disk fills up.

A break down of disk usage by user is reported on the [GPU servers dashboard][gpu-dashboard].
The dashboard can be used to find out which user might be responsible for
recent increase in disk usage. If a particular user stands out, you can contact
to find out more about their needs and ask them to remove any old data or
software they may have lying around.

[gpu-dashboard]: https://bots.dide.ic.ac.uk/grafana/d/aew654v1ovg8wc/gpu-servers?var-instance=wpia-gpu-02.dide.ic.ac.uk

In addition to using the dashboard, you can connect to the machine using `ssh
reside@wpia-gpu-02.dide.ic.ac.uk`.

The following command will show the current disk usage for `/home`:
```
df -h /home
```

The following command will list all directories in the `/home` and `/data`
directories and sort them by descending size (the `--exclude` flag is needed to
avoid double counting the bind-mount):

```sh
sudo du -x -d 1 -h /home /data --exclude /home/old-data | sort -hr
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
