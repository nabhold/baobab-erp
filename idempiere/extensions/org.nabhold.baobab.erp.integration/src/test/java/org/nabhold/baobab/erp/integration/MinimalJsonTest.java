package org.nabhold.baobab.erp.integration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Map;
import org.junit.jupiter.api.Test;

class MinimalJsonTest {

    @Test
    void parsesIntegerFields() {
        Map<String, Object> result = MinimalJson.parseObject("{\"ad_client_id\": 1000, \"ad_org_id\": 1}");
        assertEquals(1000L, result.get("ad_client_id"));
        assertEquals(1L, result.get("ad_org_id"));
    }

    @Test
    void parsesStringAndMixedFields() {
        Map<String, Object> result = MinimalJson.parseObject("{\"table\": \"C_BPartner\", \"record_id\": 1001}");
        assertEquals("C_BPartner", result.get("table"));
        assertEquals(1001L, result.get("record_id"));
    }

    @Test
    void parsesEscapedStrings() {
        Map<String, Object> result = MinimalJson.parseObject("{\"error\": \"no mapping for \\\"Party\\\"\"}");
        assertEquals("no mapping for \"Party\"", result.get("error"));
    }

    @Test
    void parsesNullAndBoolean() {
        Map<String, Object> result = MinimalJson.parseObject("{\"a\": null, \"b\": true, \"c\": false}");
        assertNull(result.get("a"));
        assertEquals(Boolean.TRUE, result.get("b"));
        assertEquals(Boolean.FALSE, result.get("c"));
    }

    @Test
    void parsesEmptyObject() {
        assertEquals(Map.of(), MinimalJson.parseObject("{}"));
    }

    @Test
    void parsesFloatingPointNumbers() {
        Map<String, Object> result = MinimalJson.parseObject("{\"rate\": 7.5}");
        assertEquals(7.5, result.get("rate"));
    }

    @Test
    void rejectsTrailingGarbage() {
        assertThrows(IllegalArgumentException.class, () -> MinimalJson.parseObject("{}garbage"));
    }

    @Test
    void rejectsMalformedObject() {
        assertThrows(IllegalArgumentException.class, () -> MinimalJson.parseObject("{\"a\": 1"));
    }
}
