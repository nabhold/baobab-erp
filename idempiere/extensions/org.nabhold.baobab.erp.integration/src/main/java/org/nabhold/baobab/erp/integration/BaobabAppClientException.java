package org.nabhold.baobab.erp.integration;

/** Raised on any failure to complete a call to baobab-app: unreachable, timed out,
 * or an unexpected (non-404) error status. */
public class BaobabAppClientException extends Exception {

    public BaobabAppClientException(String message) {
        super(message);
    }

    public BaobabAppClientException(String message, Throwable cause) {
        super(message, cause);
    }
}
