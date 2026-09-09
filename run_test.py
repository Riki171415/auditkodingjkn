import sys
import generate_word_lhr_per_rs
import generate_excel_reports_per_rs

# Patch the get_recap_desk_review to only return Adam Malik
import modules.db_manager
original_get_recap = modules.db_manager.get_recap_desk_review

def mock_get_recap():
    data = original_get_recap()
    return [r for r in data if r['kode_rs'] == '1275655']

modules.db_manager.get_recap_desk_review = mock_get_recap
# ensure the imported modules also use the mocked version
generate_word_lhr_per_rs.get_recap_desk_review = mock_get_recap
generate_excel_reports_per_rs.get_recap_desk_review = mock_get_recap

print("Testing Word Generator...")
generate_word_lhr_per_rs.generate_all_lhr_word()

print("Testing Excel Generator...")
generate_excel_reports_per_rs.generate_all_rs_excel_recap()
