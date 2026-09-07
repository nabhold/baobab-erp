package org.nabhold.baobab.erp.integration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * Exercises BaobabAppClient against a real local HTTP server (the JDK's own
 * com.sun.net.httpserver, no extra test dependency needed) reproducing exactly the
 * response shapes modules/application/server.py sends -- not a mock.
 */
class BaobabAppClientTest {

    private HttpServer server;
    private BaobabAppClient client;

    @BeforeEach
    void startServer() throws IOException {
        server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/context/resolve", exchange -> {
            String query = exchange.getRequestURI().getQuery();
            if (query != null && query.contains("entity_id=nabhold-legal")) {
                respond(exchange, 200, "{\"ad_client_id\": 1000, \"ad_org_id\": 1}");
            } else {
                respond(exchange, 404, "{\"error\": \"No active mapping\"}");
            }
        });
        server.createContext("/broken", exchange -> respond(exchange, 200, "not json"));
        server.createContext("/boom", exchange -> respond(exchange, 500, "{\"error\": \"kaboom\"}"));
        server.start();
        client = new BaobabAppClient("http://127.0.0.1:" + server.getAddress().getPort());
    }

    @AfterEach
    void stopServer() {
        server.stop(0);
    }

    private static void respond(com.sun.net.httpserver.HttpExchange exchange, int status, String body)
            throws IOException {
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().add("Content-Type", "application/json");
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(bytes);
        }
    }

    @Test
    void parsesSuccessfulResponse() throws Exception {
        Map<String, Object> result = client.get(
                "/context/resolve?tenant_id=" + BaobabAppClient.encodeQueryParam("nabhold")
                        + "&entity_id=" + BaobabAppClient.encodeQueryParam("nabhold-legal"));
        assertEquals(1000L, result.get("ad_client_id"));
        assertEquals(1L, result.get("ad_org_id"));
    }

    @Test
    void notFoundRaisesSpecificException() {
        BaobabAppNotFoundException exception = assertThrows(BaobabAppNotFoundException.class,
                () -> client.get("/context/resolve?tenant_id=x&entity_id=unknown"));
        assertTrue(exception.getMessage().contains("No active mapping"));
    }

    @Test
    void serverErrorRaisesGenericClientException() {
        BaobabAppClientException exception = assertThrows(BaobabAppClientException.class, () -> client.get("/boom"));
        assertTrue(exception.getMessage().contains("kaboom"));
    }

    @Test
    void invalidJsonBodyRaisesClientException() {
        assertThrows(BaobabAppClientException.class, () -> client.get("/broken"));
    }

    @Test
    void unreachableServerRaisesClientException() {
        BaobabAppClient unreachable = new BaobabAppClient("http://127.0.0.1:1", java.time.Duration.ofSeconds(2));
        assertThrows(BaobabAppClientException.class, () -> unreachable.get("/context/resolve"));
    }
}
