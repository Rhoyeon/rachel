        # Calculate vector score for each document
        # Initialize a dictionary to keep track of the maximum scores
        max_scores = {}  
        for doc_id, score in vector_scores.items():  
            max_scores[doc_id] = max(max_scores.get(doc_id, float('-inf')), score)  
        
        # Use max_scores instead of vector_scores going forward
        vector_scores = max_scores
