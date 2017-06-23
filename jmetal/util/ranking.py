from typing import TypeVar, List

from jmetal.util.comparator import dominance_comparator

S = TypeVar('S')


class Ranking(List[S]):
    def compute_ranking(self, solution_list: List[S]):
        pass

    def get_subfront(self, rank: int) -> List[S]:
        pass

    def get_number_of_subfronts(self) -> int:
        pass


class DominanceRanking(Ranking[List[S]]):
    def __init__(self):
        self.ranked_sublists = []

    def compute_ranking(self, solution_list: List[S]):
        # number of solutions dominating solution ith
        dominate_me = [0 for i in range(len(solution_list))]

        # list of solutions dominated by solution ith
        i_dominate = [[] for i in range(len(solution_list))]

        # front[i] contains the list of solutions belonging to front i
        front = [[] for i in range(len(solution_list)+1)]

        # Initialize the fronts
        #for i in range(0, len(solution_List)+1):
        #    self.ranked_sublists.append([])

        # Initialize the list of individuals that i dominate and the number of individuals that dominate i
        #for i in range(len(solution_List)):
        #    i_dominate.append([])
        #    dominate_me[i] = 0

        for p in range(len(solution_list)-1):
            for q in range(p+1, len(solution_list)):
                dominance_test_result = dominance_comparator(solution_list[p], solution_list[q])
                if dominance_test_result is -1:
                    i_dominate[p].append(q)
                    dominate_me[q] += 1
                elif dominance_test_result is 1:
                    i_dominate[q].append(p)
                    dominate_me[p] += 1

        for i in range(len(solution_list)):
            if dominate_me[i] is 0:
                front[0].append(i)
                solution_list[i].attributes["ranking"] = 0

        #self.ranked_sublists.append(front[0])

        i = 0
        while (len(front[i]) != 0):
            i += 1
            for p in front[i-1]:
                if p <= len(i_dominate):
                    for q in i_dominate[p]:
                        index = q
                        dominate_me[index] -= 1
                        if dominate_me[index] is 0:
                            front[i].append(index)
                            solution_list[index].attributes["ranking"] = i

        self.ranked_sublists = [[]] * i
        for j in range(i):
            Q =[0]*len(front[j])
            for k in range(len(front[j])):
                Q[k] = solution_list[front[j][k]]
                #self.ranked_sublists[j].append(solution_list[k])
            self.ranked_sublists[j] = Q

        """
        i = 0
        while len(front[i]) is not None:
            Q = []
            for p in front[i]:
                for q in i_dominate[p]:
                    dominate_me[q] -= 1
                    if dominate_me[q] == 0:
                        solution_list[q].attributes["ranking"] = i + 1
                        Q.append(q)

            i += 1
            if Q is not []:
                self.ranked_sublists.append(Q)
        """

        return self.ranked_sublists


"""
public class DominanceRanking <S extends Solution<?>>
    extends GenericSolutionAttribute<S, Integer> implements Ranking<S> {

  private static final Comparator<Solution<?>> DOMINANCE_COMPARATOR = new DominanceComparator<Solution<?>>();
  private static final Comparator<Solution<?>> CONSTRAINT_VIOLATION_COMPARATOR =
      new OverallConstraintViolationComparator<Solution<?>>();

  private List<ArrayList<S>> rankedSubPopulations;

  /**
   * Constructor
   */
  public DominanceRanking() {
    rankedSubPopulations = new ArrayList<>();
  }

  public DominanceRanking(Object id) {
    super(id) ;
    rankedSubPopulations = new ArrayList<>();
  }

  @Override
  public Ranking<S> computeRanking(List<S> solutionSet) {
    List<S> population = solutionSet;

    // dominateMe[i] contains the number of solutions dominating i
    int[] dominateMe = new int[population.size()];

    // iDominate[k] contains the list of solutions dominated by k
    List<List<Integer>> iDominate = new ArrayList<>(population.size());

    // front[i] contains the list of individuals belonging to the front i
    ArrayList<List<Integer>> front = new ArrayList<>(population.size() + 1);

    // Initialize the fronts
    for (int i = 0; i < population.size() + 1; i++) {
      front.add(new LinkedList<Integer>());
    }

    // Fast non dominated sorting algorithm
    // Contribution of Guillaume Jacquenot
    for (int p = 0; p < population.size(); p++) {
      // Initialize the list of individuals that i dominate and the number
      // of individuals that dominate me
      iDominate.add(new LinkedList<Integer>());
      dominateMe[p] = 0;
    }

    int flagDominate;
    for (int p = 0; p < (population.size() - 1); p++) {
      // For all q individuals , calculate if p dominates q or vice versa
      for (int q = p + 1; q < population.size(); q++) {
        flagDominate =
            CONSTRAINT_VIOLATION_COMPARATOR.compare(solutionSet.get(p), solutionSet.get(q));
        if (flagDominate == 0) {
          flagDominate = DOMINANCE_COMPARATOR.compare(solutionSet.get(p), solutionSet.get(q));
        }
        if (flagDominate == -1) {
          iDominate.get(p).add(q);
          dominateMe[q]++;
        } else if (flagDominate == 1) {
          iDominate.get(q).add(p);
          dominateMe[p]++;
        }
      }
    }

    for (int i = 0; i < population.size(); i++) {
      if (dominateMe[i] == 0) {
        front.get(0).add(i);
        solutionSet.get(i).setAttribute(getAttributeIdentifier(), 0);
      }
    }

    //Obtain the rest of fronts
    int i = 0;
    Iterator<Integer> it1, it2; // Iterators
    while (front.get(i).size() != 0) {
      i++;
      it1 = front.get(i - 1).iterator();
      while (it1.hasNext()) {
        it2 = iDominate.get(it1.next()).iterator();
        while (it2.hasNext()) {
          int index = it2.next();
          dominateMe[index]--;
          if (dominateMe[index] == 0) {
            front.get(i).add(index);
            //RankingAndCrowdingAttr.getAttributes(solutionSet.get(index)).setRank(i);
            solutionSet.get(index).setAttribute(getAttributeIdentifier(), i);
          }
        }
      }
    }

    rankedSubPopulations = new ArrayList<>();
    //0,1,2,....,i-1 are fronts, then i fronts
    for (int j = 0; j < i; j++) {
      rankedSubPopulations.add(j, new ArrayList<S>(front.get(j).size()));
      it1 = front.get(j).iterator();
      while (it1.hasNext()) {
        rankedSubPopulations.get(j).add(solutionSet.get(it1.next()));
      }
    }

    return this;
  }

  @Override
  public List<S> getSubfront(int rank) {
    if (rank >= rankedSubPopulations.size()) {
      throw new JMetalException("Invalid rank: " + rank + ". Max rank = " + (rankedSubPopulations.size() -1)) ;
    }
    return rankedSubPopulations.get(rank);
  }

  @Override
  public int getNumberOfSubfronts() {
    return rankedSubPopulations.size();
  }
}
"""