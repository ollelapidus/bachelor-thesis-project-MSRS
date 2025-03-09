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
    Range sum_range;
    int partition_count;
    vector<R> partition_max;

    Class(Range sum_range, vector<R> partition_max) 
    :sum_range(sum_range), partition_max(partition_max) {
        partition_count = partition_max.size();
        sort(partition_max.begin(), partition_max.end());
    }
};


void simulatedAnnealing(vector<Class> classes) {
    Range total_sum;
    for (auto c : classes) total_sum = total_sum + c.sum_range;
    int m = total_sum.low.floor();
    int cn = classes.size();

    vector<pair<int, R>> jobs;
    rep(i,0,cn) {
        for (auto x : classes[i].partition_max) {
            jobs.push_back({i, x});
        }
    }
    int n = jobs.size();
    vector<int> machine(n);
    rep(i,0,n) machine[i] = rand(m-1);
    vector<int> prio(n);
    rep(i,0,n) prio[i] = i;


    auto getScore = [](int cn, int n, int m, vector<pair<int, R>> & jobs, vector<int> & machine, vector<int> & prio) {

        vector<R> by_class(cn);
        vector<R> by_machine(m);

        vector<int> order(n);
        rep(i,0,n) order[prio[i]] = i;

        rep(i,0,n) {
            int x = order[i];
            auto [cid, sz] = jobs[x];
            int mid = machine[x];

            R place = max(by_machine[mid], by_class[cid]);
            by_machine[mid] = place + sz;
            by_class[cid] = place + sz;
        }
        
        R score(0, 1);
        rep(i,0,m) {
            score = max(score, by_machine[i]);
        }

        return score;
    };


    auto smallChange = [](int cn, int n, int m, vector<int> & machine, vector<int> & prio) {
        rep(k,0,4) {
            int i = rand(n-1);
            int j = rand(n-1);
            swap(prio[i], prio[j]);    
        }
        
        rep(k,0,4) {
            int i = rand(n - 1);
            machine[i] = rand(m - 1);
        }
    };

    double temp = 1000.;
    double cooling_rate = 0.99;
    int iterations = 10000;

    vector<int> old_machine = machine, old_prio = prio, best_machine = machine, best_prio = prio;
    R bestScore = getScore(cn, n, m, jobs, machine, prio);
    R curScore = bestScore;

    rep(iter,0,iterations) {
        smallChange(cn, n, m, machine, prio);
        R score = getScore(cn, n, m, jobs, machine, prio);

        bool change = (score <= curScore || exp(-((curScore - score).value()) / temp) > ((double) rand(1e6) / 1e6));

        if (score < bestScore) {
            cout << bestScore << endl;
            bestScore = score;
            best_machine = machine;
            best_prio = prio;
        }

        if (change) {
            curScore = score;
            old_machine = machine;
            old_prio = prio;
        }
        else {
            machine = old_machine;
            prio = old_prio;
        }

        temp *= cooling_rate;
    }

    cout << bestScore << endl;
}




int main() {
    Class c({{1,2}, {2, 3}}, {{1, 3}, {1, 2}});

    simulatedAnnealing({c, c, c, c});
}