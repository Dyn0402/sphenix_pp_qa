#ifndef READSPINDB_C

#define READSPINDB_C

#include <uspin/SpinDBContent.h>
#include <uspin/SpinDBOutput.h>

R__LOAD_LIBRARY(libuspin.so)

//////////////////////////////////////////////////////
/////  0xffff is the qa_level from XingShiftCal //////
//////////////////////////////////////////////////////
void ReadSpinDB(int runnumber = 48246, unsigned int qa_level = 0xffff)
{
  SpinDBContent spin_cont;
  SpinDBOutput spin_out("phnxrc");

  spin_out.StoreDBContent(runnumber,runnumber,qa_level);
  spin_out.GetDBContentStore(spin_cont,runnumber);
  std::cout << "Crossing angle: " << spin_cont.GetCrossAngle() << endl;
  std::cout << "Crossing angle std: " << spin_cont.GetCrossAngleStd() << endl;
  std::cout << "Crossing angle min: " << spin_cont.GetCrossAngleMin() << endl;
  std::cout << "Crossing angle max: " << spin_cont.GetCrossAngleMax() << endl;

  std::cout << "Run Number: " << runnumber << std::endl;

  ////////////////////////////////////////////////////
  // Get Bad Run QA (bad run != 0)
  int badrun = spin_cont.GetBadRunFlag();
  ////////////////////////////////////////////////////

  ////////////////////////////////////////////////////
  // Get fill number
  int fillnumber = spin_cont.GetFillNumber();
  std::cout << "Fill Number: " << fillnumber << std::endl;
  ////////////////////////////////////////////////////

  ////////////////////////////////////////////////////
  // Get crossing shift
  int crossingshift = spin_cont.GetCrossingShift();
  std::cout << "Crossing shift: " << crossingshift << std::endl;
  ////////////////////////////////////////////////////

  ////////////////////////////////////////////////////
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
  ////////////////////////////////////////////////////

  ////////////////////////////////////////////////////
  // Get beam polarizations
  double bluepol;
  double yellpol;
  double bluepolerr;
  double yellpolerr;
  spin_cont.GetPolarizationBlue(0, bluepol, bluepolerr);
  spin_cont.GetPolarizationYellow(0, yellpol, yellpolerr);
  std::cout << "Blue polarization: " << bluepol << " +/- "  << bluepolerr << std::endl;
  std::cout << "Yellow polarization: " << yellpol << " +/- "  << yellpolerr << std::endl;
  ////////////////////////////////////////////////////

  ////////////////////////////////////////////////////
  // Get MBD NS GL1p scalers
  long long mbdns[120] = {0};
  std::cout << "MBDNS GL1p scalers: [";
  for (int i = 0; i < 120; i++)
  {
    mbdns[i] = spin_cont.GetScalerMbdNoCut(i);
    std::cout << mbdns[i];
    if (i < 119)std::cout << ", ";
  }
  std::cout << "]" << std::endl;
  ////////////////////////////////////////////////////

  ////////////////////////////////////////////////////
  // Get MBD VTX GL1p scalers
  long long mbdvtx[120] = {0};
  std::cout << "MBD VTX GL1p scalers: [";
  for (int i = 0; i < 120; i++)
  {
    mbdvtx[i] = spin_cont.GetScalerMbdVertexCut(i);
    std::cout << mbdvtx[i];
    if (i < 119)std::cout << ", ";
  }
  std::cout << "]" << std::endl;
  ////////////////////////////////////////////////////

  ////////////////////////////////////////////////////
  // Get ZDC NS GL1p scalers
  long long zdcns[120] = {0};
  std::cout << "ZDC NS GL1p scalers: [";
  for (int i = 0; i < 120; i++)
  {
    zdcns[i] = spin_cont.GetScalerZdcNoCut(i);
    std::cout << zdcns[i];
    if (i < 119)std::cout << ", ";
  }
  std::cout << "]" << std::endl;
  ////////////////////////////////////////////////////

}

#endif
