(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.9543cff1d806f553.js","sha256":"9543cff1d806f553fbabf41ddbeaed1f0405e61dcc6836c4ee328573bce969d9","count":244});
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
