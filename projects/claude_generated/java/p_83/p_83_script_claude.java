package com.example.xml;

import jakarta.xml.bind.*;
import jakarta.xml.bind.annotation.*;
import java.io.*;
import java.util.*;

@XmlRootElement(name = "library")
@XmlAccessorType(XmlAccessType.FIELD)
class Library {
    @XmlElement(name = "book")
    private List<Book> books = new ArrayList<>();

    public Library() {}
    public List<Book> getBooks() { return books; }
    public void setBooks(List<Book> books) { this.books = books; }
    public void addBook(Book book) { this.books.add(book); }
}

@XmlAccessorType(XmlAccessType.FIELD)
class Book {
    @XmlElement private String isbn;
    @XmlElement private String title;
    @XmlElement private Author author;
    @XmlElement private int year;
    @XmlElement private double price;

    public Book() {}
    public Book(String isbn, String title, Author author, int year, double price) {
        this.isbn = isbn;
        this.title = title;
        this.author = author;
        this.year = year;
        this.price = price;
    }

    public String getIsbn() { return isbn; }
    public void setIsbn(String isbn) { this.isbn = isbn; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public Author getAuthor() { return author; }
    public void setAuthor(Author author) { this.author = author; }
    public int getYear() { return year; }
    public void setYear(int year) { this.year = year; }
    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }

    @Override
    public String toString() {
        return String.format("Book{isbn='%s', title='%s', author=%s, year=%d, price=%.2f}",
                isbn, title, author, year, price);
    }
}

@XmlAccessorType(XmlAccessType.FIELD)
class Author {
    @XmlElement private String name;
    @XmlElement private String country;

    public Author() {}
    public Author(String name, String country) {
        this.name = name;
        this.country = country;
    }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getCountry() { return country; }
    public void setCountry(String country) { this.country = country; }

    @Override
    public String toString() {
        return String.format("Author{name='%s', country='%s'}", name, country);
    }
}

public class XMLParser {
    public static <T> void marshal(T object, String outputPath) throws JAXBException {
        JAXBContext context = JAXBContext.newInstance(object.getClass());
        Marshaller marshaller = context.createMarshaller();
        marshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, true);
        marshaller.marshal(object, new File(outputPath));
        System.out.println("XML written to: " + outputPath);
    }

    public static <T> String marshalToString(T object) throws JAXBException {
        JAXBContext context = JAXBContext.newInstance(object.getClass());
        Marshaller marshaller = context.createMarshaller();
        marshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, true);
        StringWriter writer = new StringWriter();
        marshaller.marshal(object, writer);
        return writer.toString();
    }

    public static <T> T unmarshal(String inputPath, Class<T> clazz) throws JAXBException {
        JAXBContext context = JAXBContext.newInstance(clazz);
        Unmarshaller unmarshaller = context.createUnmarshaller();
        return clazz.cast(unmarshaller.unmarshal(new File(inputPath)));
    }

    public static <T> T unmarshalFromString(String xml, Class<T> clazz) throws JAXBException {
        JAXBContext context = JAXBContext.newInstance(clazz);
        Unmarshaller unmarshaller = context.createUnmarshaller();
        return clazz.cast(unmarshaller.unmarshal(new StringReader(xml)));
    }

    public static void main(String[] args) {
        try {
            // Create library with books
            Library library = new Library();
            library.addBook(new Book("978-0-123456-47-2", "Effective Java",
                    new Author("Joshua Bloch", "USA"), 2018, 45.99));
            library.addBook(new Book("978-0-987654-32-1", "Clean Code",
                    new Author("Robert Martin", "USA"), 2008, 39.99));
            library.addBook(new Book("978-1-234567-89-0", "Design Patterns",
                    new Author("Gang of Four", "Various"), 1994, 54.99));

            // Marshal to XML
            System.out.println("=== Marshalling to XML ===");
            marshal(library, "library.xml");

            // Marshal to String
            String xmlString = marshalToString(library);
            System.out.println("\nXML Content:\n" + xmlString);

            // Unmarshal from XML
            System.out.println("\n=== Unmarshalling from XML ===");
            Library loadedLibrary = unmarshal("library.xml", Library.class);
            System.out.println("Loaded " + loadedLibrary.getBooks().size() + " books:");
            for (Book book : loadedLibrary.getBooks()) {
                System.out.println("  " + book);
            }

        } catch (JAXBException e) {
            e.printStackTrace();
        }
    }
}
