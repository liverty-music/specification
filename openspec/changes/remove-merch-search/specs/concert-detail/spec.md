## REMOVED Requirements

### Requirement: Merch Info Link in Concert Detail

**Reason**: The `Series.merch_url` field is removed, so the concert detail sheet no longer has a merchandise link to render. Production data showed the resolved link was usually a generic storefront/homepage rather than a tour-specific goods page, offering no value beyond the existing official-info link.

**Migration**: None. The "View Merch Info / グッズ情報を見る" link, its `eventDetail.viewMerch` i18n keys, the `hasMerchUrl` gate, and the `merchUrl` client entity field are removed. The official-info link is unchanged.
