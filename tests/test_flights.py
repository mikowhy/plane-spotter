from planespotter.flights import Aircraft


class TestAircraftFromStateVector:
    def test_parses_state_vector(self) -> None:
        state_vector = [
            "abc123",  # 0: icao24
            "LOT123  ",  # 1: callsign (with whitespace)
            "Poland",  # 2: origin_country
            1234567890,  # 3: time_position
            1234567890,  # 4: last_contact
            16.863,  # 5: longitude
            52.404,  # 6: latitude
            300.0,  # 7: baro_altitude
            False,  # 8: on_ground
            70.0,  # 9: velocity
            288.0,  # 10: true_track
            -3.0,  # 11: vertical_rate
            None,  # 12: sensors
            310.0,  # 13: geo_altitude
            "1234",  # 14: squawk
            False,  # 15: spi
            0,  # 16: position_source
        ]
        aircraft = Aircraft.from_state_vector(state_vector)
        assert aircraft.icao24 == "abc123"
        assert aircraft.callsign == "LOT123"
        assert aircraft.origin_country == "Poland"
        assert aircraft.longitude == 16.863
        assert aircraft.latitude == 52.404
        assert aircraft.baro_altitude == 300.0
        assert aircraft.on_ground is False
        assert aircraft.velocity == 70.0
        assert aircraft.true_track == 288.0
        assert aircraft.vertical_rate == -3.0
        assert aircraft.geo_altitude == 310.0
        assert aircraft.squawk == "1234"

    def test_none_callsign(self) -> None:
        state_vector = [
            "abc123",
            None,
            "Poland",
            0,
            0,
            16.0,
            52.0,
            300.0,
            False,
            70.0,
            288.0,
            -3.0,
            None,
            310.0,
            None,
            False,
            0,
        ]
        aircraft = Aircraft.from_state_vector(state_vector)
        assert aircraft.callsign is None


class TestAircraftToDict:
    def test_roundtrip(self) -> None:
        aircraft = Aircraft(
            icao24="abc123",
            callsign="TEST",
            origin_country="Poland",
            longitude=16.0,
            latitude=52.0,
            baro_altitude=300.0,
            on_ground=False,
            velocity=70.0,
            true_track=288.0,
            vertical_rate=-3.0,
            geo_altitude=310.0,
            squawk=None,
        )
        result = aircraft.to_dict()
        assert result["icao24"] == "abc123"
        assert result["callsign"] == "TEST"
        assert result["squawk"] is None
        assert len(result) == 12
