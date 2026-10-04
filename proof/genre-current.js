(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.0a384b66008eb8e7.js","sha256":"0a384b66008eb8e7f7a09a13766748c9fddf9d22edb37073dcae3ece46700b31","count":244});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeGenreManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:genre-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:genre-data-error", {detail:{reason:"genre data unavailable"}}));
  };
  document.head.appendChild(script);
}());
