# Step 4 -- OpenSky Network API

## Endpoint

```
GET https://opensky-network.org/api/states/all?lamin=52.35&lamax=52.50&lomin=16.75&lomax=16.95
```

## Rate Limits

| Tier               | Credits/Day | Time Resolution |
|--------------------|-------------|-----------------|
| Anonymous          | 400         | 10 seconds      |
| Registered         | 4,000       | 5 seconds       |
| Active contributor | 8,000       | 5 seconds       |

At 400 credits/day anonymous, polling every 15s gives ~1.7 hours continuous. Register for free to get 4,000/day (~16.7 hours).

## Authentication

Since mid-March 2025, new accounts use **OAuth2 client credentials** (not basic auth):

1. Create API client at opensky-network.org to get `client_id` + `client_secret`
2. Request token from: `https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token`
3. Tokens expire after 30 minutes
4. Use header: `Authorization: Bearer $TOKEN`

**Recommendation:** Start anonymous, register if needed.

## Response Format

```json
{
  "time": 1709654400,
  "states": [
    ["3c6444", "DLH1234 ", "Germany", 1709654398, 1709654399, 16.82, 52.42, 1500.0, false, 120.5, 270.0, -2.5, null, 1524.0, "1000", false, 0, 0]
  ]
}
```

### State Vector Fields

| Index | Field           | Type   | Unit                                |
|-------|-----------------|--------|-------------------------------------|
| 0     | icao24          | string | hex                                 |
| 1     | callsign        | string | 8 chars, nullable                   |
| 2     | origin_country  | string |                                     |
| 3     | time_position   | int    | Unix timestamp, nullable            |
| 4     | last_contact    | int    | Unix timestamp                      |
| 5     | longitude       | float  | degrees, nullable                   |
| 6     | latitude        | float  | degrees, nullable                   |
| 7     | baro_altitude   | float  | **meters**, nullable                |
| 8     | on_ground       | bool   |                                     |
| 9     | velocity        | float  | **m/s**, nullable                   |
| 10    | true_track      | float  | degrees from north, nullable        |
| 11    | vertical_rate   | float  | **m/s**, nullable                   |
| 12    | sensors         | int[]  | nullable                            |
| 13    | geo_altitude    | float  | **meters**, nullable                |
| 14    | squawk          | string | nullable                            |
| 15    | spi             | bool   |                                     |
| 16    | position_source | int    | 0=ADS-B, 1=ASTERIX, 2=MLAT, 3=FLARM |
| 17    | category        | int    | 0-20                                |

## Alternatives (if OpenSky is down)

- **dump1090 + RTL-SDR dongle** (~$25) -- direct ADS-B reception, no API dependency, best for fixed location
- **ADS-B Exchange** (via RapidAPI) -- $10/month, unfiltered data
- **FlightAware AeroAPI** -- paid, professional-grade
