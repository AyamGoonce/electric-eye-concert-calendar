(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7e914ef1dd34c5a8.js","sha256":"7e914ef1dd34c5a8801fd493149b890c1e015f28d94f93b2e5a63cd62c2d7e9c","count":2452,"publishedAt":"2026-09-14T11:57:51Z","state":"calendar-state.json","stateSha256":"4f42c68c17683677de11d4dad80d24cb20b090d18abe485f555456eaf2e84396"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
