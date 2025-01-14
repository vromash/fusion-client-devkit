import fusion
from fusion.rest import ApiException

from utils import get_fusion_config, wait_operation_succeeded


def teardown_workloads():
    print("Tearing down workloads")

    # create an API client with your access Configuration
    config = get_fusion_config()
    client = fusion.ApiClient(config)

    # get needed API clients
    t = fusion.TenantsApi(api_client=client)
    ts = fusion.TenantSpacesApi(api_client=client)
    pg = fusion.PlacementGroupsApi(api_client=client)
    v = fusion.VolumesApi(api_client=client)
    ss = fusion.SnapshotsApi(api_client=client)
    hap = fusion.HostAccessPoliciesApi(api_client=client)

    # Get all Tenants
    try:
        t_list = t.list_tenants()
        # pprint(t_list)
    except ApiException as e:
        raise RuntimeError("Exception when calling TenantsApi->list_tenants") from e

    for tenant in t_list.items:
        # Get all Tenant Spaces in the Tenant
        try:
            ts_list = ts.list_tenant_spaces(tenant.name)
            # pprint(ts_list)
        except ApiException as e:
            raise RuntimeError("Exception when calling TenantSpacesApi->list_tenant_spaces") from e

        for tenant_space in ts_list.items:
            # Get all Volumes in the Tenant Space
            try:
                v_list = v.list_volumes(tenant.name, tenant_space.name)
                # pprint(v_list)
            except ApiException as e:
                raise RuntimeError("Exception when calling VolumesApi->list_volumes") from e

            for volume in v_list.items:
                # Detach all Host Access Policies from Volume
                print("Detaching host access policies from volume", volume.name, "in tenant space", tenant_space.name, "in tenant", tenant.name)
                vol_patch = fusion.VolumePatch(host_access_policies=fusion.NullableString(""))
                try:
                    api_response = v.update_volume(vol_patch, tenant.name, tenant_space.name, volume.name)
                    # pprint(api_response)
                    wait_operation_succeeded(api_response.id, client)
                except ApiException as e:
                    raise RuntimeError("Exception when calling VolumesApi->update_volume") from e

                # Destroy volume (two-step volume deletion is enforced in Fusion, thus, volume has to be destroyed first, and eradicated then)
                print("Destroying volume", volume.name, "in tenant space", tenant_space.name, "in tenant", tenant.name)
                try:
                    patch = fusion.VolumePatch(destroyed=fusion.NullableBoolean(True))
                    api_response = v.update_volume(patch, tenant.name, tenant_space.name, volume.name)
                    # pprint(api_response)
                    wait_operation_succeeded(api_response.id, client)
                except ApiException as e:
                    raise RuntimeError("Exception when calling VolumesApi->update_volume") from e

                # Delete Volume
                print("Eradicating volume", volume.name, "in tenant space", tenant_space.name, "in tenant", tenant.name)
                try:
                    api_response = v.delete_volume(tenant.name, tenant_space.name, volume.name)
                    # pprint(api_response)
                    wait_operation_succeeded(api_response.id, client)
                except ApiException as e:
                    raise RuntimeError("Exception when calling VolumesApi->delete_volume") from e

            # Get all Snapshots in the Tenant Space
            try:
                ss_list = ss.list_snapshots(tenant.name, tenant_space.name)
                # pprint(ss_list)
            except ApiException as e:
                raise RuntimeError("Exception when calling SnapshotsApi->list_snapshots") from e

            for snapshot in ss_list.items:
                # Delete Snapshot
                print("Deleting snapshot", snapshot.name, "in tenant space", tenant_space.name, "in tenant", tenant.name)
                try:
                    api_response = ss.delete_snapshot(tenant.name, tenant_space.name, snapshot.name)
                    # pprint(api_response)
                    wait_operation_succeeded(api_response.id, client)
                except ApiException as e:
                    raise RuntimeError("Exception when calling SnapshotsApi->delete_snapshot") from e

            # Get all Placement Groups in the Tenant Space
            try:
                pg_list = pg.list_placement_groups(tenant.name, tenant_space.name)
                # pprint(pg_list)
            except ApiException as e:
                raise RuntimeError("Exception when calling PlacementGroupsApi->list_placement_groups") from e

            for placement_group in pg_list.items:
                # Delete Placement Group
                print("Deleting placement group", placement_group.name, "in tenant space", tenant_space.name, "in tenant", tenant.name)
                try:
                    api_response = pg.delete_placement_group(tenant.name, tenant_space.name, placement_group.name)
                    # pprint(api_response)
                    wait_operation_succeeded(api_response.id, client)
                except ApiException as e:
                    raise RuntimeError("Exception when calling PlacementGroupsApi->delete_placement_group") from e

            # Delete Tenant Space
            print("Deleting tenant space", tenant_space.name, "in tenant", tenant.name)
            try:
                api_response = ts.delete_tenant_space(tenant.name, tenant_space.name)
                # pprint(api_response)
                wait_operation_succeeded(api_response.id, client)
            except ApiException as e:
                raise RuntimeError("Exception when calling TenantSpaceApi->delete_tenant_space") from e

    # Get Host Access Policies
    try:
        hap_list = hap.list_host_access_policies()
        # pprint(hap_list)
    except ApiException as e:
        raise RuntimeError("Exception when calling HostAccessPoliciesApi->list_host_access_policies") from e

    for host_access_policy in hap_list.items:
        # Delete Host Access Policy
        print("Deleting host access policy", host_access_policy.name)
        try:
            api_response = hap.delete_host_access_policy(host_access_policy.name)
            # pprint(api_response)
            wait_operation_succeeded(api_response.id, client)
        except ApiException as e:
            raise RuntimeError("Exception when calling HostAccessPoliciesApi->delete_host_access_policy") from e

    print("Done tearing down workloads!")


if __name__ == '__main__':
    teardown_workloads()
