package org.nabhold.baobab.erp.mapping;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.nabhold.baobab.erp.integration.BaobabAppClient;
import org.nabhold.baobab.erp.mapping.CanonicalMappingResolver.MappingNotFoundException;
import org.nabhold.baobab.erp.mapping.CanonicalMappingResolver.NativeRecordRef;

/**
 * Exercises BaobabMappingResolver against a real local HTTP server reproducing
 * baobab-app's /mapping/resolve and /mapping/resolve-canonical response shapes.
 */
class BaobabMappingResolverTest {

    private static final String CANONICAL_ID = "e4a8ccd4-21cb-43b7-915f-1434d9aef07a";

    private HttpServer server;
    private BaobabMappingResolver resolver;

    @BeforeEach
    void startServer() throws IOException {
        server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/mapping/resolve", exchange -> {
            String query = exchange.getRequestURI().getQuery();
            if (query != null && query.contains("tenant_id=nabhold") && query.contains(CANONICAL_ID)) {
                respond(exchange, 200, "{\"table\": \"C_BPartner\", \"record_id\": 1001}");
            } else {
                respond(exchange, 404, "{\"error\": \"No active mapping\"}");
            }
        });
        server.createContext("/mapping/resolve-canonical", exchange -> {
            String query = exchange.getRequestURI().getQuery();
            if (query != null && query.contains("tenant_id=nabhold") && query.contains("record_id=1001")) {
                respond(exchange, 200, "{\"canonical_id\": \"" + CANONICAL_ID + "\"}");
            } else {
                respond(exchange, 404, "{\"error\": \"No active mapping\"}");
            }
        });
        server.start();
        BaobabAppClient client = new BaobabAppClient("http://127.0.0.1:" + server.getAddress().getPort());
        resolver = new BaobabMappingResolver(client);
    }

    @AfterEach
    void stopServer() {
        server.stop(0);
    }

    private static void respond(com.sun.net.httpserver.HttpExchange exchange, int status, String body)
            throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(bytes);
        }
    }

    @Test
    void resolvesToNativeOverHttp() throws Exception {
        NativeRecordRef ref = resolver.resolveToNative("nabhold", "Party", CANONICAL_ID);
        assertEquals(new NativeRecordRef("C_BPartner", 1001), ref);
    }

    @Test
    void resolvesToCanonicalOverHttp() throws Exception {
        String canonicalId = resolver.resolveToCanonical("nabhold", "C_BPartner", 1001);
        assertEquals(CANONICAL_ID, canonicalId);
    }

    @Test
    void missingNativeMappingFailsClosed() {
        assertThrows(MappingNotFoundException.class, () -> resolver.resolveToNative("nabhold", "Party", "unknown"));
    }

    @Test
    void crossTenantLookupFailsClosed() {
        assertThrows(MappingNotFoundException.class,
                () -> resolver.resolveToNative("thamani", "Party", CANONICAL_ID));
    }

    @Test
    void missingCanonicalMappingFailsClosed() {
        assertThrows(MappingNotFoundException.class,
                () -> resolver.resolveToCanonical("nabhold", "C_BPartner", 999999));
    }
}
