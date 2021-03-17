# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['UI.py'],
             pathex=['/home/max/Documents/github/testhub/COMP0016_2020_21_Team35'],
             binaries=[],
             datas=[('/usr/local/lib/python3.8/dist-packages/librosa/util/example_data', 'librosa/util/example_data')],
             hiddenimports=['sklearn.utils._weight_vector', 'scipy.special.cython_special'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='UI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
