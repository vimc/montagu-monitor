# PackitConfigDrift

This alert is raised when the configuration that is deployed onto one of the
NixOS-based hosts does not match the state of the main branch of the
[`reside-ic/packit-infra` repository][packit-infra].

The packit-infra repository holds a declarative configuration of the operating
system. Under normal operation, all NixOS machines should be deployed from the
main branch of this repository. However it is possible for the machines to
become out of sync with the repository. There are two main scenarios when this
may happen:

- A pull-request is merged into the main branch of the repository and is not
  deployed to the machine.
- A branch is deployed to the machine and is not merged to main (or is merged
  with further modifications).

Both of these conditions are generally harmless, and these are in fact expected
to happen transiently as part of the normal develop-test-merge-deploy cycle.
For this reason, the alert only fires after a week of divergence.

They do however become an issue if left unaddressed for an extended period of
time. Over time context is forgotten and it becomes unclear why a given
machine's actual state does not match expectations. This leads to uncertainty
and doubt when new changes need to be deployed.

## Diagnosis

Resolving the alert can be as simple as re-deploying the main branch to the
affected server. However before doing so it is important to compare the
expected and actual configurations to make sure we understand the situtation
and are not, for example, rolling back important changes.

There are two ways we can compare the configuration: we can compare the source
Nix files or we can compare the result of their evaluation. Comparing the
source is generally more readable and easier to understand, but it requires
access to the exact commit that was used to deploy to the server.

### Comparing configuration sources

The first step is to identify the Git revision of the configuration that was
last deployed to the server.  This is exposed in [Prometheus][prometheus] as
the `revision` label of the `nixos_configuration_info` metric.

If the `revision` label ends with the `-dirty` suffix then the configuration
was deployed from a dirty Git working directory and the revision shown is not a
true representative of the configuration that was deployed. Similarly, even if
the worktree was clean and the revision does not have a `-dirty` suffix, if the
commit in question was never pushed to GitHub it may not be available for
comparison.  In either cases, one must fall back to comparing the evaluated
derivation, as explained below.

If however the revision is not dirty and is available on GitHub (or in a local
clone of the repository), one can use the usual Git tools to compare the two
revisions. For example, use the GitHub interface to compare the commits,
replacing `<REV>` with the commit hash that was obtained from the metric:
`https://github.com/reside-ic/packit-infra/compare/main..<REV>`. GitHub
supports ["two-dot" and "three-dot" comparisons][two-dots] - in this context
using a two-dot comparison is generally preferable.

### Comparing configuration evaluations

If the original source used to deploy the configuration is not available any
more, as a last resort one can compare the evaluated derivation instead.

The `packit-infra` repository includes a tool that can do this. The following
command will connect to the given host, retrieve its evaluated configuration,
then locally evaluate the configuration from the main branch and print the
differences using the [`nix-diff`][nix-diff] tool. You should replace
`<hostname>` with the appropriate hostname (eg. wpia-packit-dev).

```sh
nix run --refresh github:reside-ic/packit-infra#diff <hostname>
```

Depending on the changes that were made, the output of the command may be very
verbose and contain lots of repetitive changes (eg. if base packages were
updated).

## Resolution

Assuming there aren't any unexpected changes requiring special care, resolving
the alert can be done by re-deploying the main branch to the machine (again
replacing `<hostname>` as appropriate):

```sh
nix run --refresh github:reside-ic/packit-infra#deploy <hostname>
```

[prometheus]: https://bots.dide.ic.ac.uk/prometheus
[packit-infra]: https://github.com/reside-ic/packit-infra
[nix-diff]: https://github.com/Gabriella439/nix-diff
[two-dots]: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-comparing-branches-in-pull-requests#three-dot-and-two-dot-git-diff-comparisons
