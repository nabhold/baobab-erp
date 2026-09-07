package org.nabhold.baobab.erp.context;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.nabhold.baobab.erp.context.ContextResolver.ContextResolutionException;
import org.nabhold.baobab.erp.context.ContextResolver.ResolvedContext;
import org.nabhold.baobab.erp.integration.BaobabAppClient;

/**
 * Exercises BaobabContextResolver against a real local HTTP server reproducing
 * baobab-app's /context/resolve response shapes exactly.
 */
class BaobabContextResolverTest {

    private HttpServer server;
    private BaobabContextResolver resolver;

    @BeforeEach
    void startServer() throws IOException {
        server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/context/resolve", exchange -> {
            String query = exchange.getRequestURI().getQuery();
            if (query != null && query.contains("tenant_id=nabhold") && query.contains("entity_id=nabhold-legal")) {
                respond(exchange, 200, "{\"ad_client_id\": 1000, \"ad_org_id\": 1}");
            } else {
                respond(exchange, 404, "{\"error\": \"No active mapping\"}");
            }
        });
        server.start();
        BaobabAppClient client = new BaobabAppClient("http://127.0.0.1:" + server.getAddress().getPort());
        resolver = new BaobabContextResolver(client);
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
    void resolvesRealContextOverHttp() throws Exception {
        ResolvedContext context = resolver.resolve("nabhold", "nabhold-legal");
        assertEquals(new ResolvedContext(1000, 1), context);
    }

    @Test
    void unmappedPairFailsClosed() {
        assertThrows(ContextResolutionException.class, () -> resolver.resolve("nabhold", "unknown-legal-entity"));
    }

    @Test
    void crossTenantPairFailsClosed() {
        // NABHOLD -> THAMANI must never resolve: distinct tenants stay isolated.
        assertThrows(ContextResolutionException.class, () -> resolver.resolve("thamani", "nabhold-legal"));
    }

    @Test
    void blankInputsFailClosedWithoutCallingTheNetwork() {
        assertThrows(ContextResolutionException.class, () -> resolver.resolve("", "nabhold-legal"));
        assertThrows(ContextResolutionException.class, () -> resolver.resolve("nabhold", null));
    }

    @Test
    void unreachableBackendFailsClosedNotSilently() {
        BaobabContextResolver unreachable = new BaobabContextResolver(new BaobabAppClient("http://127.0.0.1:1"));
        ContextResolutionException exception =
                assertThrows(ContextResolutionException.class, () -> unreachable.resolve("nabhold", "nabhold-legal"));
        assertTrue(exception.getMessage().contains("Could not resolve context"));
    }
}
