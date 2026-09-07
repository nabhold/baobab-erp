package org.nabhold.baobab.erp.integration;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Parses exactly the flat JSON object shapes baobab-app's endpoints return --
 * string, number, boolean, and null values, no nesting or arrays. Not a general
 * JSON parser; deliberately narrow so it needs no dependency embedded into this
 * OSGi bundle. Numbers are returned as {@link Long} or {@link Double} depending on
 * whether a decimal point/exponent is present.
 */
final class MinimalJson {

    private final String text;
    private int position;

    private MinimalJson(String text) {
        this.text = text;
    }

    static Map<String, Object> parseObject(String text) {
        MinimalJson parser = new MinimalJson(text);
        parser.skipWhitespace();
        Map<String, Object> result = parser.readObject();
        parser.skipWhitespace();
        if (!parser.atEnd()) {
            throw new IllegalArgumentException("Unexpected trailing content in JSON: " + text);
        }
        return result;
    }

    private Map<String, Object> readObject() {
        expect('{');
        Map<String, Object> result = new LinkedHashMap<>();
        skipWhitespace();
        if (peek() == '}') {
            position++;
            return result;
        }
        while (true) {
            skipWhitespace();
            String key = readString();
            skipWhitespace();
            expect(':');
            skipWhitespace();
            Object value = readValue();
            result.put(key, value);
            skipWhitespace();
            char next = peek();
            if (next == ',') {
                position++;
                continue;
            }
            if (next == '}') {
                position++;
                break;
            }
            throw new IllegalArgumentException("Expected ',' or '}' at position " + position + " in: " + text);
        }
        return result;
    }

    private Object readValue() {
        char c = peek();
        if (c == '"') {
            return readString();
        }
        if (c == '-' || Character.isDigit(c)) {
            return readNumber();
        }
        if (text.startsWith("true", position)) {
            position += 4;
            return Boolean.TRUE;
        }
        if (text.startsWith("false", position)) {
            position += 5;
            return Boolean.FALSE;
        }
        if (text.startsWith("null", position)) {
            position += 4;
            return null;
        }
        throw new IllegalArgumentException("Unexpected value at position " + position + " in: " + text);
    }

    private String readString() {
        expect('"');
        StringBuilder builder = new StringBuilder();
        while (true) {
            char c = next();
            if (c == '"') {
                break;
            }
            if (c == '\\') {
                char escaped = next();
                switch (escaped) {
                    case '"' -> builder.append('"');
                    case '\\' -> builder.append('\\');
                    case '/' -> builder.append('/');
                    case 'n' -> builder.append('\n');
                    case 't' -> builder.append('\t');
                    case 'r' -> builder.append('\r');
                    case 'b' -> builder.append('\b');
                    case 'f' -> builder.append('\f');
                    case 'u' -> {
                        String hex = text.substring(position, position + 4);
                        position += 4;
                        builder.append((char) Integer.parseInt(hex, 16));
                    }
                    default -> throw new IllegalArgumentException("Unknown escape '\\" + escaped + "'");
                }
            } else {
                builder.append(c);
            }
        }
        return builder.toString();
    }

    private Object readNumber() {
        int start = position;
        if (peek() == '-') {
            position++;
        }
        boolean isFloatingPoint = false;
        while (!atEnd() && (Character.isDigit(peek()) || peek() == '.' || peek() == 'e' || peek() == 'E'
                || peek() == '+' || peek() == '-')) {
            if (peek() == '.' || peek() == 'e' || peek() == 'E') {
                isFloatingPoint = true;
            }
            position++;
        }
        String number = text.substring(start, position);
        return isFloatingPoint ? (Object) Double.parseDouble(number) : (Object) Long.parseLong(number);
    }

    private void skipWhitespace() {
        while (!atEnd() && Character.isWhitespace(peek())) {
            position++;
        }
    }

    private void expect(char c) {
        if (atEnd() || peek() != c) {
            throw new IllegalArgumentException("Expected '" + c + "' at position " + position + " in: " + text);
        }
        position++;
    }

    private char peek() {
        if (atEnd()) {
            throw new IllegalArgumentException("Unexpected end of JSON input: " + text);
        }
        return text.charAt(position);
    }

    private char next() {
        if (atEnd()) {
            throw new IllegalArgumentException("Unexpected end of JSON input: " + text);
        }
        return text.charAt(position++);
    }

    private boolean atEnd() {
        return position >= text.length();
    }
}
