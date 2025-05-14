using namespace std;
#include <bits/stdc++.h>

#define rep(i,a,b) for(int i = a; i < b; i++)
typedef long long ll;
typedef vector<int> vi;
typedef vector<vi> vvi;
typedef vector<vvi> vvvi;

mt19937 rng(6215);
ll rand(ll maxr) {
    return uniform_int_distribution<ll>(0, maxr)(rng);
}

struct R {
    // Rational number
    ll p, q;

    void simplify() {
        // Always keep on form gcd(p, q) = 1, q > 0.

        ll g = gcd(p, q);
        p /= g;
        q /= g;
        if (q < 0) {
            p *= -1;
            q *= -1;
        }
    }

    R(ll p, ll q) :p(p), q(q) {simplify();}
    R() {p = 0, q = 1;}

    R operator+(const R b) const {return R(p * b.q + b.p * q, q * b.q);}
    R operator-(const R b) const {return *this+R(-b.p, b.q);}
    R operator*(const R b) const {return R(p * b.p, q * b.q);}
    R operator/(const R b) const {return R(p * b.q, q * b.p);}
    bool operator==(const R b) const {return (*this-b).p==0;}
    bool operator>(const R b) const {return (*this-b).p>0;}
    bool operator>=(const R b) const {return (*this-b).p>=0;}
    bool operator<(const R b) const {return (*this-b).p<0;}
    bool operator<=(const R b) const {return (*this-b).p<=0;}

    int ceil() {return (p+q-1) / q;}
    int floor() {return p / q;}
    double value() {return (double)p/q;}
};

struct Range {
    R low, high;
    Range(R low, R high) :low(low), high(high) {}
    Range() {}
    Range operator+(Range b) {return Range(low + b.low, high + b.high);}
};

ostream& operator<<(ostream& os, const R& r)
{
    if (r.q == 1) os << "R[" << r.p << "]";
    else os << "R[" << r.p << "/" << r.q << "]";
    return os;
}

ostream& operator<<(ostream& os, const Range& r)
{
    os << "Range[" << r.low << ", " << r.high << "]";
    return os;
}

struct Class {
    R load;
    int job_count;
    vector<R> job_sz;

    Class(vector<R> job_sz) 
    :job_sz(job_sz) {
        job_count = job_sz.size();
        sort(job_sz.begin(), job_sz.end());
        load = R(0, 1);
        for (auto x : job_sz) load = load + x;
    }
};

R RES(100, 1);


void simulatedAnnealing(vector<Class> classes, int m, bool write = false) {
    int cn = classes.size();

    vector<pair<int, R>> jobs;
    rep(i,0,cn) {
        for (auto x : classes[i].job_sz) {
            jobs.push_back({i, x});
        }
    }
    int n = jobs.size();
    vector<int> prio(n);
    rep(i,0,n) prio[i] = i;


    struct Score {
        R makespan;

        R value() {
            return makespan;
        }
    };


    auto getScore = [](int cn, int n, int m, vector<pair<int, R>> & jobs, vector<int> & prio) {
        Score score;

        vector<int> last_placed_on_machine(m, -1); // which class?
        vector<R> machine_load(m);

        vector<int> order(n);
        rep(i,0,n) order[prio[i]] = i;

        rep(i,0,n) {
            int x = order[i];
            auto [cid, sz] = jobs[x];

            int mid = 0;
            rep(j,0,m) {
                if (last_placed_on_machine[j] == cid) {
                    mid = j;
                    break;
                }
                if (machine_load[j] < machine_load[mid]) mid = j;
            }

            R place = machine_load[mid];
            machine_load[mid] = machine_load[mid] + sz;
            score.makespan = max(score.makespan, machine_load[mid]);
            last_placed_on_machine[mid] = cid;
        }


        RES = min(RES, score.makespan);
        return score.value();
    };




    auto swapTwo = [](int cn, int n, int m, vector<int> & prio) {
        int i = rand(n-1);
        int j = rand(n-1);
        swap(prio[i], prio[j]);    
    };

    auto swapPrioClass = [](int cn, int n, int m, const vector<pair<int, R>> & jobs, vector<int> & prio) {
        int cid = rand(cn-1);

        vector<int> affect;
        rep(i,0,n) if (jobs[i].first == cid) affect.push_back(i);

        rep(_,0,3) {
            int i = affect[rand(affect.size()-1)];
            int j = affect[rand(affect.size()-1)];
            swap(prio[i], prio[j]);
        }
    };

    auto bigChange = [](int cn, int n, int m, vector<int> & prio) {
        shuffle(prio.begin(), prio.end(), rng);
    };

    auto smallChange = [](int cn, int n, int m, vector<int> & prio) {
        rep(k,0,10) {
            int i = rand(n-1);
            int j = rand(n-1);
            swap(prio[i], prio[j]);    
        }
    };



    auto change = [&](int cn, int n, int m, const vector<pair<int, R>> & jobs, vector<int> & prio) {
        if (rand(10) == 0) bigChange(cn, n, m, prio);
        else if (rand(2)==0) swapPrioClass(cn, n, m, jobs, prio);
        else if (rand(1)) swapTwo(cn, n, m, prio);
        else smallChange(cn, n, m, prio);
    };



    double temp = 1.;
    double cooling_rate = 0.99999;
    int iterations = 500000;

    vector<int> old_prio = prio, best_prio = prio;
    R bestScore = getScore(cn, n, m, jobs, prio);
    R curScore = bestScore;

    int ccnt = 0, cnt = 0;
    rep(iter,0,iterations) {
        change(cn, n, m, jobs, prio);
        R score = getScore(cn, n, m, jobs, prio);

        double prob = (double) rand(1e6) / 1e6;
        bool change = ((score < curScore) || (exp(-((score - curScore).value()) / temp) > prob));
        cnt++;
        ccnt += change;
        if (score < bestScore) {
            cout << score << endl;
            bestScore = score;
            best_prio = prio;
        }

        if (change) {
            curScore = score;
            old_prio = prio;
        }
        else {
            prio = old_prio;
        }

        temp *= cooling_rate;
    }
    cout << R(ccnt, cnt) << endl;

    auto writePlacement = [](int cn, int n, int m, vector<pair<int, R>> & jobs, vector<int> & prio) {
        vector<int> last_placed_on_machine(m, -1); // which class?
        vector<R> machine_load(m);

        vector<int> order(n);
        rep(i,0,n) order[prio[i]] = i;
        

        cout << n << " " << m << endl;
        rep(i,0,n) {
            int x = order[i];
            auto [cid, sz] = jobs[x];

            int mid = 0;
            rep(j,0,m) {
                if (last_placed_on_machine[j] == cid) {
                    mid = j;
                    break;
                }
                if (machine_load[j] < machine_load[mid]) mid = j;
            }



            cout << machine_load[mid].value() << " " << mid << " " << sz.value() << " " << cid << endl; 
            machine_load[mid] = machine_load[mid] + sz;
            last_placed_on_machine[mid] = cid;
        }
    };

    if (write) writePlacement(cn, n, m, jobs, best_prio);

    cout << RES << endl;
}




int main() {
    int m; 
    cin >> m;

    map<int,vector<int>> class_map;

    int sz, cid;
    while (cin >> sz >> cid) {
        if (class_map.find(cid) == class_map.end()) {
            class_map[cid] = {};
        }
        class_map[cid].push_back(sz);
    }

    vector<Class> classes;
    for (auto [cid, list] : class_map) {
        vector<R> job_sz;
        for (auto x : list) job_sz.push_back(R(x, 1));
        classes.push_back(Class(job_sz));
    }


    simulatedAnnealing(classes, m, true);
}

