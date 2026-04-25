from sqlalchemy import text

from common.database import engine

STATEMENTS = [
    """
    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'aleksei_user_service')
    EXEC('CREATE SCHEMA aleksei_user_service');
    """,
    """
    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'aleksei_competition_service')
    EXEC('CREATE SCHEMA aleksei_competition_service');
    """,
    """
    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'aleksei_recipe_service')
    EXEC('CREATE SCHEMA aleksei_recipe_service');
    """,
    """
    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'aleksei_feedback_service')
    EXEC('CREATE SCHEMA aleksei_feedback_service');
    """,
    """
    IF OBJECT_ID('aleksei_user_service.users', 'U') IS NULL
    CREATE TABLE aleksei_user_service.users (
        id INT PRIMARY KEY,
        name NVARCHAR(255) NOT NULL,
        email NVARCHAR(255) NOT NULL UNIQUE,
        created_at DATETIME2 NOT NULL
    );
    """,
    """
    IF OBJECT_ID('aleksei_competition_service.competitions', 'U') IS NULL
    CREATE TABLE aleksei_competition_service.competitions (
        id INT PRIMARY KEY,
        title NVARCHAR(255) NOT NULL,
        description NVARCHAR(MAX) NOT NULL,
        start_date DATETIME2 NOT NULL,
        end_date DATETIME2 NOT NULL,
        status NVARCHAR(50) NOT NULL
    );
    """,
    """
    IF OBJECT_ID('aleksei_recipe_service.categories', 'U') IS NULL
    CREATE TABLE aleksei_recipe_service.categories (
        id INT PRIMARY KEY,
        name NVARCHAR(255) NOT NULL UNIQUE
    );
    """,
    """
    IF OBJECT_ID('aleksei_recipe_service.recipes', 'U') IS NULL
    CREATE TABLE aleksei_recipe_service.recipes (
        id INT PRIMARY KEY,
        title NVARCHAR(255) NOT NULL,
        description NVARCHAR(MAX) NOT NULL,
        author_id INT NOT NULL,
        category_id INT NOT NULL,
        CONSTRAINT FK_recipe_author FOREIGN KEY (author_id)
            REFERENCES aleksei_user_service.users(id),
        CONSTRAINT FK_recipe_category FOREIGN KEY (category_id)
            REFERENCES aleksei_recipe_service.categories(id)
    );
    """,
    """
    IF OBJECT_ID('aleksei_recipe_service.ingredients', 'U') IS NULL
    CREATE TABLE aleksei_recipe_service.ingredients (
        id INT PRIMARY KEY,
        recipe_id INT NOT NULL,
        name NVARCHAR(255) NOT NULL,
        quantity NVARCHAR(255) NOT NULL,
        CONSTRAINT FK_ingredient_recipe FOREIGN KEY (recipe_id)
            REFERENCES aleksei_recipe_service.recipes(id)
    );
    """,
    """
    IF OBJECT_ID('aleksei_competition_service.entries', 'U') IS NULL
    CREATE TABLE aleksei_competition_service.entries (
        id INT PRIMARY KEY,
        competition_id INT NOT NULL,
        user_id INT NOT NULL,
        recipe_id INT NOT NULL,
        status NVARCHAR(50) NOT NULL,
        CONSTRAINT FK_entry_competition FOREIGN KEY (competition_id)
            REFERENCES aleksei_competition_service.competitions(id),
        CONSTRAINT FK_entry_user FOREIGN KEY (user_id)
            REFERENCES aleksei_user_service.users(id),
        CONSTRAINT FK_entry_recipe FOREIGN KEY (recipe_id)
            REFERENCES aleksei_recipe_service.recipes(id),
        CONSTRAINT UQ_entry_competition_user UNIQUE (competition_id, user_id)
    );
    """,
    """
    IF OBJECT_ID('aleksei_feedback_service.feedback', 'U') IS NULL
    CREATE TABLE aleksei_feedback_service.feedback (
        id INT PRIMARY KEY,
        entry_id INT NOT NULL,
        user_id INT NOT NULL,
        comment NVARCHAR(MAX) NOT NULL,
        created_at DATETIME2 NOT NULL,
        CONSTRAINT FK_feedback_entry FOREIGN KEY (entry_id)
            REFERENCES aleksei_competition_service.entries(id),
        CONSTRAINT FK_feedback_user FOREIGN KEY (user_id)
            REFERENCES aleksei_user_service.users(id)
    );
    """,
    """
    IF OBJECT_ID('aleksei_feedback_service.ratings', 'U') IS NULL
    CREATE TABLE aleksei_feedback_service.ratings (
        id INT PRIMARY KEY,
        entry_id INT NOT NULL,
        user_id INT NOT NULL,
        score INT NOT NULL,
        CONSTRAINT FK_rating_entry FOREIGN KEY (entry_id)
            REFERENCES aleksei_competition_service.entries(id),
        CONSTRAINT FK_rating_user FOREIGN KEY (user_id)
            REFERENCES aleksei_user_service.users(id),
        CONSTRAINT UQ_rating_entry_user UNIQUE (entry_id, user_id)
    );
    """,
    """
    IF NOT EXISTS (SELECT 1 FROM aleksei_user_service.users)
    BEGIN
        INSERT INTO aleksei_user_service.users (id, name, email, created_at)
        VALUES
            (1, 'Alice Johnson', 'alice@example.com', '2026-01-10T10:00:00'),
            (2, 'Bob Smith', 'bob@example.com', '2026-01-15T12:00:00'),
            (3, 'Charlie Brown', 'charlie@example.com', '2026-02-01T09:00:00');
    END;
    """,
    """
    IF NOT EXISTS (SELECT 1 FROM aleksei_competition_service.competitions)
    BEGIN
        INSERT INTO aleksei_competition_service.competitions
            (id, title, description, start_date, end_date, status)
        VALUES
            (1, 'Spring Bake-Off 2026', 'Annual spring baking competition',
             '2026-03-01T00:00:00', '2026-03-31T23:59:59', 'Active'),
            (2, 'Pasta Masters', 'Best homemade pasta challenge',
             '2026-04-01T00:00:00', '2026-04-30T23:59:59', 'Upcoming'),
            (3, 'Appetizer Showdown', 'Creative appetizer competition',
             '2026-02-01T00:00:00', '2026-02-28T23:59:59', 'Completed');
    END;
    """,
    """
    IF NOT EXISTS (SELECT 1 FROM aleksei_recipe_service.categories)
    BEGIN
        INSERT INTO aleksei_recipe_service.categories (id, name)
        VALUES
            (1, 'Desserts'),
            (2, 'Main Course'),
            (3, 'Appetizers');
    END;
    """,
    """
    IF NOT EXISTS (SELECT 1 FROM aleksei_recipe_service.recipes)
    BEGIN
        INSERT INTO aleksei_recipe_service.recipes
            (id, title, description, author_id, category_id)
        VALUES
            (1, 'Chocolate Lava Cake', 'Rich molten chocolate cake', 1, 1),
            (2, 'Truffle Carbonara', 'Classic carbonara with truffle oil', 2, 2),
            (3, 'Bruschetta Trio', 'Three varieties of bruschetta', 3, 3),
            (4, 'Tiramisu', 'Classic Italian tiramisu', 1, 1);
    END;
    """,
    """
    IF NOT EXISTS (SELECT 1 FROM aleksei_recipe_service.ingredients)
    BEGIN
        INSERT INTO aleksei_recipe_service.ingredients (id, recipe_id, name, quantity)
        VALUES
            (1, 1, 'Dark Chocolate', '200g'),
            (2, 1, 'Butter', '100g'),
            (3, 1, 'Eggs', '3 pcs'),
            (4, 2, 'Spaghetti', '400g'),
            (5, 2, 'Guanciale', '150g'),
            (6, 2, 'Truffle Oil', '2 tbsp'),
            (7, 3, 'Baguette', '1 pc'),
            (8, 3, 'Tomatoes', '4 pcs'),
            (9, 4, 'Mascarpone', '500g'),
            (10, 4, 'Espresso', '300ml');
    END;
    """,
    """
    IF NOT EXISTS (SELECT 1 FROM aleksei_competition_service.entries)
    BEGIN
        INSERT INTO aleksei_competition_service.entries
            (id, competition_id, user_id, recipe_id, status)
        VALUES
            (1, 1, 1, 1, 'Submitted'),
            (2, 1, 2, 2, 'Submitted'),
            (3, 3, 3, 3, 'Approved'),
            (4, 2, 1, 4, 'Pending');
    END;
    """,
    """
    IF NOT EXISTS (SELECT 1 FROM aleksei_feedback_service.feedback)
    BEGIN
        INSERT INTO aleksei_feedback_service.feedback
            (id, entry_id, user_id, comment, created_at)
        VALUES
            (1, 3, 1, 'Amazing appetizer presentation!', '2026-03-01T10:00:00'),
            (2, 3, 2, 'Very creative combinations.', '2026-03-01T11:00:00'),
            (3, 1, 3, 'Delicious chocolate cake!', '2026-03-15T14:00:00');
    END;
    """,
    """
    IF NOT EXISTS (SELECT 1 FROM aleksei_feedback_service.ratings)
    BEGIN
        INSERT INTO aleksei_feedback_service.ratings
            (id, entry_id, user_id, score)
        VALUES
            (1, 3, 1, 9),
            (2, 3, 2, 8),
            (3, 1, 3, 10);
    END;
    """,
]


def main() -> None:
    with engine.begin() as conn:
        for statement in STATEMENTS:
            conn.execute(text(statement))
    print("Database schemas, tables, and stub data are ready.")


if __name__ == "__main__":
    main()
