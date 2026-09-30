package com.example.demo;

import org.springframework.batch.item.ItemProcessor;

public class UserProcessor implements ItemProcessor<User, User> {

    @Override
    public User process(final User user) throws Exception {
        final String name = user.getName().toUpperCase();
        final String email = user.getEmail().toLowerCase();

        final User transformedUser = new User(name, email);
        System.out.println("Converting (" + user + ") into (" + transformedUser + ")");

        // Simulate a failure for demonstration purposes
        if (transformedUser.getName().equals("JANE SMITH")) {
            throw new RuntimeException("Simulated processing error for Jane Smith");
        }

        return transformedUser;
    }
}
