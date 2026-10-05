import { SupportedLanguage } from '../types';

export interface SampleSnippet {
  name: string;
  language: SupportedLanguage;
  description: string;
  code: string;
}

export const SAMPLE_SNIPPETS: SampleSnippet[] = [
  {
    name: 'Python: Vulnerable Query & Logic Bug',
    language: 'python',
    description: 'Demonstrates SQL concatenation, bare except, and unbounded complexity.',
    code: `import sqlite3

def get_user_data(user_id, raw_query):
    # Potential SQL Injection vulnerability
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
    cursor.execute(query)
    
    # Inefficient nested iteration
    results = []
    for row in cursor.fetchall():
        for item in raw_query:
            if item in row:
                results.append(row)
                
    try:
        eval(user_id)  # Critical security risk
    except:
        pass  # Bare except suppresses unexpected bugs
        
    return results
`
  },
  {
    name: 'JavaScript: DOM XSS & Loose Equality',
    language: 'javascript',
    description: 'Demonstrates innerHTML usage, loose equality, and eval.',
    code: `function renderUserProfile(containerId, userInput) {
  const container = document.getElementById(containerId);
  
  // Potential XSS vulnerability
  container.innerHTML = "<div>Welcome, " + userInput.name + "</div>";
  
  // Type coercion hazard
  if (userInput.role == 0) {
    console.log("Guest privileges assigned");
  }
  
  // Insecure dynamic evaluation
  if (userInput.calcExpr) {
    var computed = eval(userInput.calcExpr);
    console.log("Result:", computed);
  }
}
`
  },
  {
    name: 'TypeScript: Array Deduplication & Strict Check',
    language: 'typescript',
    description: 'Modern TypeScript function with O(N) complexity.',
    code: `interface ItemRecord {
  id: string;
  score: number;
  tags: string[];
}

export function deduplicateAndRank(items: ItemRecord[]): ItemRecord[] {
  const seen = new Set<string>();
  const uniqueItems: ItemRecord[] = [];

  for (const item of items) {
    if (!seen.has(item.id)) {
      seen.add(item.id);
      uniqueItems.push(item);
    }
  }

  // Stable sort in descending order of score
  return uniqueItems.sort((a, b) => b.score - a.score);
}
`
  },
  {
    name: 'C: Buffer Overflow Vulnerability',
    language: 'c',
    description: 'Demonstrates legacy unsafe functions gets() and strcpy().',
    code: `#include <stdio.h>
#include <string.h>

void process_input() {
    char buffer[64];
    printf("Enter authorization token: ");
    
    // Critical buffer overflow hazard: gets() has no bounds checking
    gets(buffer);
    
    char dest[32];
    // Dangerous unbounded string copy
    strcpy(dest, buffer);
    
    printf("Processed token: ");
    printf(dest); // Format string vulnerability
}

int main() {
    process_input();
    return 0;
}
`
  },
  {
    name: 'C++: Memory Leak & Pointer Safety',
    language: 'cpp',
    description: 'Manual memory allocation without RAII deallocation.',
    code: `#include <iostream>
#include <vector>

class DataProcessor {
public:
    void processData(int size) {
        // Raw heap allocation without free/delete
        int* rawArray = new int[size];
        
        for (int i = 0; i < size; ++i) {
            rawArray[i] = i * 2;
        }
        
        std::cout << "Data processed successfully." << std::endl;
        // Missing delete[] rawArray -> Memory Leak
    }
};

int main() {
    DataProcessor dp;
    dp.processData(100);
    return 0;
}
`
  },
  {
    name: 'Java: SQL Concatenation & Exception Swallowing',
    language: 'java',
    description: 'Demonstrates Statement SQL concatenation and printStackTrace().',
    code: `import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
import java.sql.ResultSet;

public class UserManager {
    public void authenticateUser(String username, String password) {
        try {
            Connection conn = DriverManager.getConnection("jdbc:mysql://localhost:3306/db", "root", "pass");
            Statement stmt = conn.createStatement();
            
            // Critical SQL Injection vulnerability
            String sql = "SELECT * FROM accounts WHERE user = '" + username + "' AND pass = '" + password + "'";
            ResultSet rs = stmt.executeQuery(sql);
            
            while (rs.next()) {
                System.out.println("Authorized: " + rs.getString("email"));
            }
        } catch (Exception e) {
            // Anti-pattern: generic exception caught and raw trace printed
            e.printStackTrace();
        }
    }
}
`
  }
];
