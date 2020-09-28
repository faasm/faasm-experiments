#include <util/environment.h>
#include <util/files.h>
#include <util/logging.h>
#include <util/macros.h>
#include <util/strings.h>

#include <storage/SparseMatrixFileSerialiser.h>

#include <eigen3/Eigen/Sparse>

#include <boost/filesystem.hpp>
#include <string>

// NOTE - these are also hard-coded in the actual SVM function and must match
#define REUTERS_N_FEATURES 47236
#define REUTERS_N_EXAMPLES 781265
#define REUTERS_N_EXAMPLES_MICRO 128

using namespace boost::filesystem;

/**
 * The reuters data consists of a list of articles with categories assigned to
 * them. Each article is given a weight for each of a set of features.
 */
void parseReutersData(const path& downloadDir,
                      const path& outputDir,
                      long nExamples)
{
    const std::shared_ptr<spdlog::logger>& logger = util::getLogger();

    // Use the test set for training (as Hogwild does)
    std::vector<std::string> files = { "test" };

    int exampleIdx = 0;
    int maxFeature = 0;

    std::vector<Eigen::Triplet<double>> triplets;
    std::vector<double> categories(nExamples);
    std::vector<int> featureCounts(REUTERS_N_FEATURES);

    // Dataset is split across multiple files
    for (const auto& f : files) {
        path thisFile = downloadDir;
        thisFile.append(f);
        logger->info("Reading from {} ", thisFile.c_str());

        std::ifstream input(thisFile.c_str());

        std::string line;
        while (getline(input, line) && exampleIdx < nExamples) {
            // Split up the line
            const std::vector<std::string> lineTokens =
              util::splitString(line, ' ');

            // Treat the classification value for this article as a double to
            // ease serialisation/ deserialisation
            double cat = std::stod(lineTokens[0]);
            categories.at(exampleIdx) = cat;

            // Iterate through the feature weights for this example (there will
            // be one to many) They are split as <feature>:<weight>
            for (int i = 1; i < lineTokens.size(); i++) {
                // Ignore empty token
                std::basic_string<char> thisToken = lineTokens[i];
                if (util::isAllWhitespace(thisToken)) {
                    continue;
                }

                // Split up index:value part
                const std::vector<std::string> valueTokens =
                  util::splitString(thisToken, ':');
                int feature = std::stoi(valueTokens[0]);
                double weight = std::stod(valueTokens[1]);

                // Add to matrix
                triplets.emplace_back(
                  Eigen::Triplet<double>(feature, exampleIdx, weight));

                // Record an occurrence of this feature
                featureCounts.at(feature)++;

                maxFeature = std::max(maxFeature, feature);
            };

            // Move onto next example
            exampleIdx++;
        }

        // Close off the file
        input.close();
    }

    // Note, features are zero based
    int nFeatures = maxFeature + 1;
    if (nExamples == REUTERS_N_EXAMPLES && nFeatures != REUTERS_N_FEATURES) {
        logger->error(
          "Expected {} features but got {}", REUTERS_N_FEATURES, maxFeature);
    }

    if (categories.size() != nExamples) {
        logger->error(
          "Got {} categories but {} examples", categories.size(), nExamples);
    }

    logger->info("Totals: {} features and {} examples", maxFeature, exampleIdx);

    // Build the sparse matrix (row for each feature, col for each example)
    Eigen::SparseMatrix<double> inputsMatrix(nFeatures, exampleIdx);
    inputsMatrix.setFromTriplets(triplets.begin(), triplets.end());

    // Write input matrix to files
    storage::SparseMatrixFileSerialiser s(inputsMatrix);
    s.writeToFile(outputDir.string());

    // Write categories to file
    size_t nCatBytes = categories.size() * sizeof(double);
    auto catPtr = BYTES(categories.data());
    path catFile = outputDir;
    catFile.append("outputs");

    logger->info("Writing {} bytes to {}", nCatBytes, catFile.c_str());
    util::writeBytesToFile(catFile.string(),
                           std::vector<uint8_t>(catPtr, catPtr + nCatBytes));

    // Write feature counts to file
    long nFeatureCountBytes = featureCounts.size() * sizeof(int);
    auto featureCountsPtr = BYTES(featureCounts.data());

    path featureCountsFile = outputDir;
    featureCountsFile.append("feature_counts");

    logger->info(
      "Writing {} bytes to {}", nFeatureCountBytes, featureCountsFile.c_str());
    util::writeBytesToFile(
      featureCountsFile.string(),
      std::vector<uint8_t>(featureCountsPtr,
                           featureCountsPtr + nFeatureCountBytes));
}

int main()
{
    util::initLogging();
    const std::shared_ptr<spdlog::logger>& logger = util::getLogger();

    path faasmDir(util::getEnvVar("HOME", ""));
    faasmDir.append("faasm");

    path downloadDir = faasmDir;
    downloadDir.append("rcv1");

    path outputDir = faasmDir;
    outputDir.append("data/reuters");
    path microOutputDir = faasmDir;
    microOutputDir.append("data/reuters_micro");

    if (exists(outputDir)) {
        remove_all(outputDir);
    }
    if (exists(microOutputDir)) {
        remove_all(microOutputDir);
    }

    if (!exists(downloadDir)) {
        logger->error("RCV1 data does not exist at {}", downloadDir.string());
        return 1;
    }

    create_directories(outputDir);
    create_directories(microOutputDir);

    parseReutersData(downloadDir, outputDir, REUTERS_N_EXAMPLES);
    parseReutersData(downloadDir, microOutputDir, REUTERS_N_EXAMPLES_MICRO);

    return 0;
}
