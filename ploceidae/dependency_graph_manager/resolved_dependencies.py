import attr

@attr.s
class ResolvedDependencies(object):
    all_resolved_dependencies      = attr.ib()
    resolved_dependencies          = attr.ib()
    resolved_dependencies_by_group = attr.ib()