package main

import (
	"context"
	"log"
	"net/http"

	"github.com/google/go-github/v68/github"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	metricGithubRateLimit = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "github_exporter_rate_limit",
		Help: "The maximum number of requests that can be made per hour",
	})
	metricGithubRateRemaining = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "github_exporter_rate_remaining",
		Help: "The number of requests remaining in the current rate limit window",
	})
	metricGithubRateReset = prometheus.NewGauge(prometheus.GaugeOpts{
		Name: "github_exporter_rate_reset",
		Help: "The time at which the current rate limit window resets, in UTC epoch seconds",
	})
	metricScrapesTotal = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "github_exporter_scrapes_total",
		Help: "Total number of attempted scrapes",
	})
	metricFailedScrapesTotal = prometheus.NewCounter(prometheus.CounterOpts{
		Name: "github_exporter_failed_scrapes_total",
		Help: "Total number of failed scrapes",
	})
)

func init() {
	prometheus.MustRegister(metricGithubRateLimit)
	prometheus.MustRegister(metricGithubRateRemaining)
	prometheus.MustRegister(metricGithubRateReset)
	prometheus.MustRegister(metricScrapesTotal)
	prometheus.MustRegister(metricFailedScrapesTotal)
}

func Scrape(ctx context.Context, client *github.Client, owner string, repo string, registry *prometheus.Registry) (err error) {
	log.Printf("Scraping metrics from repository '%s/%s'", owner, repo)
	metricScrapesTotal.Inc()

	defer func() {
		if err != nil {
			log.Printf("Scrape failed: %v", err)
			metricFailedScrapesTotal.Inc()
		}
	}()

	opt := &github.BranchListOptions{}
	metricGithubRepoBranchInfo := prometheus.NewGaugeVec(prometheus.GaugeOpts{
		Name:        "github_repo_branch_info",
		Help:        "Information about each branch of the repository",
		ConstLabels: prometheus.Labels{"owner": owner, "repo": repo},
	}, []string{"branch", "sha"})

	if err := registry.Register(metricGithubRepoBranchInfo); err != nil {
		return err
	}

	for {
		branches, resp, err := client.Repositories.ListBranches(ctx, owner, repo, opt)
		if err != nil {
			return err
		}
		for _, b := range branches {
			metricGithubRepoBranchInfo.WithLabelValues(*b.Name, *b.Commit.SHA).Set(1)
		}
		metricGithubRateLimit.Set(float64(resp.Rate.Limit))
		metricGithubRateRemaining.Set(float64(resp.Rate.Remaining))
		metricGithubRateReset.Set(float64(resp.Rate.Reset.GetTime().Unix()))

		if resp.NextPage == 0 {
			break
		}
		opt.Page = resp.NextPage
	}

	return nil
}

func ScrapeHandler(client *github.Client) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		query := r.URL.Query()
		owner := query.Get("owner")
		repo := query.Get("repo")
		if owner == "" || repo == "" {
			http.Error(w, "owner and/or repo query parameters missing", http.StatusBadRequest)
			return
		}

		registry := prometheus.NewRegistry()
		err := Scrape(r.Context(), client, owner, repo, registry)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		h := promhttp.HandlerFor(registry, promhttp.HandlerOpts{})
		h.ServeHTTP(w, r)
	})
}

func main() {
	client := github.NewClient(nil)
	http.Handle("/metrics", promhttp.Handler())
	http.Handle("GET /scrape", ScrapeHandler(client))
	log.Fatal(http.ListenAndServe(":8080", nil))
}
