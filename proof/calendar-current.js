(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.263e38c6d2b45825.js","sha256":"263e38c6d2b45825ae397216793d41537abd1d76d2f415d7f78a31f64adba4fe","count":1841,"publishedAt":"2026-08-26T13:45:57Z","state":"calendar-state.json","stateSha256":"71db9cde2b4522fc017fb30f553e8409f66d69c3b475f3ee1cbf9ffe7fa4a12c"});
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
