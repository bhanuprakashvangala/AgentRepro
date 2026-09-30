package com.example.demo.service;

import com.example.demo.entity.Book;
import com.example.demo.exception.ResourceNotFoundException;
import com.example.demo.repository.BookRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class BookService {

    private final BookRepository bookRepository;

    public BookService(BookRepository bookRepository) {
        this.bookRepository = bookRepository;
    }

    public List<Book> findAll() {
        return bookRepository.findAll();
    }

    public Book findById(Long id) {
        return bookRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Book not found with id " + id));
    }

    public Book create(Book book) {
        return bookRepository.save(book);
    }

    public Book update(Long id, Book payload) {
        Book existing = findById(id);
        existing.setTitle(payload.getTitle());
        existing.setAuthor(payload.getAuthor());
        existing.setPages(payload.getPages());
        return bookRepository.save(existing);
    }

    public void delete(Long id) {
        Book existing = findById(id);
        bookRepository.delete(existing);
    }
}
