#include <iostream>
#include <vector>

#include <uspin/SpinDBContent.h>
#include <uspin/SpinDBOutput.h>


void PrintRunParameters(const SpinDBContent &spinContent, bool get_crossing_angle_info = false) {
    std::cout << "Run Number: " << spinContent.GetRunNumber() << std::endl;
    std::cout << "QA Level: " << spinContent.GetQALevel() << std::endl;
    std::cout << "Fill Number: " << spinContent.GetFillNumber() << std::endl;
    std::cout << "Bad Run: " << spinContent.GetBadRunFlag() << std::endl;

    // Get spin patterns
    int bluespin[120] = {0};
    int yellspin[120] = {0};
    std::cout << "Blue spin pattern: [";
    for (int i = 0; i < 120; i++)
    {
    bluespin[i] = spin_cont.GetSpinPatternBlue(i);
    std::cout << bluespin[i];
    if (i < 119)std::cout << ", ";
    }
    std::cout << "]" << std::endl;

    std::cout << "Yellow spin pattern: [";
    for (int i = 0; i < 120; i++)
    {
    yellspin[i] = spin_cont.GetSpinPatternYellow(i);
    std::cout << yellspin[i];
    if (i < 119)std::cout << ", ";
    }
    std::cout << "]" << std::endl;

    if (get_crossing_angle_info) {
        std::cout << "Cross Angle: " << spinContent.GetCrossAngle() << std::endl;
        std::cout << "Cross Angle Std: " << spinContent.GetCrossAngleStd() << std::endl;
        std::cout << "Cross Angle Min: " << spinContent.GetCrossAngleMin() << std::endl;
        std::cout << "Cross Angle Max: " << spinContent.GetCrossAngleMax() << std::endl;
    }
}

int spindb_test() {
    std::vector<int> run_numbers = {42581, 45409, 49307, 51337, 54280};
    bool read_crossing_angle_info = false;

    unsigned int qa_level = 0xffff;

    for (int run_number : run_numbers) {
        SpinDBOutput dbOutput("phnxrc");
        spin_out.StoreDBContent(run_number,run_number,qa_level);
        spin_out.GetDBContentStore(spin_cont,run_number);
        SpinDBContent spinContent;
        odbc::ResultSet *rs = dbOutput.GetResultSetForRun(run_number); // Assuming this method exists
        if (rs != nullptr) {
            dbOutput.GetDBContent(spinContent, rs);
            PrintRunParameters(spinContent, read_crossing_angle_info);
            delete rs;
        } else {
            std::cout << "Failed to retrieve data for run number: " << run_number << std::endl;
        }
    }

    return 0;
}