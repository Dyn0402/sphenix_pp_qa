#include <iostream>
#include <vector>

#include <uspin/SpinDBContent.h>
#include <uspin/SpinDBOutput.h>


void PrintRunParameters(SpinDBContent &spin_content, bool get_crossing_angle_info = false) {
    std::cout << "Run Number: " << spin_content.GetRunNumber() << std::endl;
    std::cout << "QA Level: " << spin_content.GetQALevel() << std::endl;
    std::cout << "Fill Number: " << spin_content.GetFillNumber() << std::endl;
    std::cout << "Bad Run: " << spin_content.GetBadRunFlag() << std::endl;

    // Get spin patterns
    int bluespin[120] = {0};
    int yellspin[120] = {0};
    std::cout << "Blue spin pattern: [";
    for (int i = 0; i < 120; i++)
    {
    bluespin[i] = spin_content.GetSpinPatternBlue(i);
    std::cout << bluespin[i];
    if (i < 119)std::cout << ", ";
    }
    std::cout << "]" << std::endl;

    std::cout << "Yellow spin pattern: [";
    for (int i = 0; i < 120; i++)
    {
    yellspin[i] = spin_content.GetSpinPatternYellow(i);
    std::cout << yellspin[i];
    if (i < 119)std::cout << ", ";
    }
    std::cout << "]" << std::endl;

    if (get_crossing_angle_info) {
        std::cout << "Cross Angle: " << spin_content.GetCrossAngle() << std::endl;
        std::cout << "Cross Angle Std: " << spin_content.GetCrossAngleStd() << std::endl;
        std::cout << "Cross Angle Min: " << spin_content.GetCrossAngleMin() << std::endl;
        std::cout << "Cross Angle Max: " << spin_content.GetCrossAngleMax() << std::endl;
    }
}

int spindb_test() {
    std::vector<int> run_numbers = {42581, 45409, 49307, 51337, 54280};
    bool read_crossing_angle_info = false;

    unsigned int qa_level = 0xffff;

    for (int run_number : run_numbers) {
        SpinDBOutput dbOutput("phnxrc");
        SpinDBContent spin_content;

        spin_out.StoreDBContent(run_number,run_number,qa_level);
        spin_out.GetDBContentStore(spin_content,run_number);

        odbc::ResultSet *rs = dbOutput.GetResultSetForRun(run_number); // Assuming this method exists
        if (rs != nullptr) {
            dbOutput.GetDBContent(spin_content, rs);
            PrintRunParameters(spin_content, read_crossing_angle_info);
            delete rs;
        } else {
            std::cout << "Failed to retrieve data for run number: " << run_number << std::endl;
        }
    }

    return 0;
}