package org.nabhold.baobab.erp.integration;

/** baobab-app answered 404: the resource genuinely doesn't exist (no active mapping,
 * no such record), as distinct from {@link BaobabAppClientException}'s "couldn't even
 * get an answer". Callers translate this into their own fail-closed exception rather
 * than retrying or guessing. */
public class BaobabAppNotFoundException extends BaobabAppClientException {

    public BaobabAppNotFoundException(String message) {
        super(message);
    }
}
